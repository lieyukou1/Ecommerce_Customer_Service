from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path
from urllib import error, request


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1"
INPUT_DIR = DATASET_ROOT / "reduced_round03_base_v1"
OUTPUT_DIR = DATASET_ROOT / "reduced_round03_aug_v1"
PROJECT_ENV_PATH = REPO_ROOT / "customer-service-backend" / ".env"
DEFAULT_OPENAI_BASE_URL = "https://jsyai.xinglian.work"
DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"

TARGET_BUCKETS = {
    "ambiguous_all_null": {"train": 80, "val": 20},
    "active_task_slot_fill": {"train": 80, "val": 20},
    "task_interrupt_resume_cancel": {"train": 80, "val": 20},
    "directive_exit_runtime": {"train": 40, "val": 10},
    "work_order_business_urge": {"train": 30, "val": 8},
    "work_order_business_complaint": {"train": 30, "val": 8},
}

ALLOWED_OUTPUT_KEYS = {"task", "knowledge", "chitchat", "directive"}
ALLOWED_TASK_COMMANDS = {"start_flow", "resume_flow", "cancel_flow", "set_slots"}

BANNED_PATTERNS = [
    "这是投诉原因补充",
    "这是催办原因补充",
    "我是在补催办原因",
    "我是在补投诉原因",
    "我是在补充投诉原因",
    "我是在确认具体服务项目",
    "我是在补联系电话",
    "别默认进入办理",
    "先按规则说明来",
    "围绕这个规则本身",
    "顺着刚才的话题再补充一下",
    "按这单本身回答就行",
    "别串到别的工单",
    "别切到别的工单",
    "我想换个话题，我想换个话题",
]

SUSPICIOUS_PATTERNS = [
    "比如帮我",
    "比如把",
    "比如远程",
    "我是在补",
    "这是.*补充",
    "别切到别的",
    "别查到别的",
]

GENERATION_SYSTEM_PROMPT = """你是“物业客服 TurnPlan reduced round_03 定向扩样器”。

你的任务是：基于给定的 runtime 状态、output 标签和一个锚点样本，生成一条新的、自然的中文客服训练样本。

硬约束：
1. 绝对不能修改 output。
2. 绝对不能修改 runtime_state / active_task / active_system_task / paused_tasks / focused_object。
3. 只能生成：
   - input.history
   - input.user_message
4. history 和 user_message 必须让原 output 仍然成立。
5. 只输出合法 JSON：
   {
     "history": [{"role": "...", "text": "..."}],
     "user_message": "...",
     "generation_notes": ["..."]
   }

自然度要求：
- 不要写模板拼接腔，不要出现“比如帮我……”“那你先看着办吧，比如……”。
- 不要让用户自我标注意图，例如“这是投诉原因补充”“我是在补催办原因”。
- 不要让用户使用系统内部术语，例如“别切到别的工单”“按这单本身回答”。
- 用户可以模糊、着急、口语化、半句补充，但不能把标签直接说出来。
- assistant 历史轮次也要自然，不要总是“好的/明白/可以”三板斧；要像真实接话。
- 除非锚点语义强依赖，否则不要照抄原句；要换成新的自然表达。
- 不要编造和 focused_object 明显无关的新业务事实；例如对象是“书房网口无信号”，就不要扯到空调不制冷。

bucket 重点：
- ambiguous_all_null：用户是在求助，但信息还不足以唯一确定 flow 或 intent；允许模糊。
- active_task_slot_fill：用户只补当前槽位内容，不解释自己在补什么。
- task_interrupt_resume_cancel：要像真实改主意、继续、取消，不要显式说 resume/cancel。
- directive_exit_runtime：像自然结束当前话题，简短一些。
- work_order_business_urge：用户表达着急、催办诉求，原因藏在自然抱怨里。
- work_order_business_complaint：用户表达不满、要投诉，原因藏在自然抱怨里。
"""

REVIEW_SYSTEM_PROMPT = """你是“物业客服 TurnPlan reduced round_03 样本审稿器”。

你会收到一条候选样本，请检查：
1. history / user_message 是否像真实用户和客服说话。
2. 是否含有模板拼接、自我标注意图、系统内部术语。
3. 是否保留了原 output 可成立的语义。
4. 是否编造了与 focused_object 明显不一致的新事实。
4. 是否和给定的 seen_user_messages 过于接近或重复。

只输出合法 JSON：
{
  "pass": true,
  "issues": [],
  "advice": []
}
"""


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    env: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def default_model_pool() -> list[dict]:
    pool: list[dict] = []
    external_key = os.environ.get("TURNPLAN_LLM_API_KEY")
    external_base_url = os.environ.get("TURNPLAN_LLM_BASE_URL", DEFAULT_OPENAI_BASE_URL)
    external_model = os.environ.get("TURNPLAN_LLM_MODEL", DEFAULT_OPENAI_MODEL)
    if external_key:
        pool.append(
            {
                "alias": "xinglian_openai",
                "model": external_model,
                "base_url": external_base_url,
                "api_key": external_key,
            }
        )

    project_env = load_dotenv(PROJECT_ENV_PATH)
    deepseek_key = project_env.get("LLM_API_KEY")
    deepseek_base_url = project_env.get("LLM_BASE_URL")
    deepseek_model = project_env.get("LLM_MODEL")
    if deepseek_key and deepseek_base_url and deepseek_model:
        pool.append(
            {
                "alias": "project_deepseek",
                "model": deepseek_model,
                "base_url": deepseek_base_url,
                "api_key": deepseek_key,
            }
        )
    return pool


def choose_model(record_key: str, model_pool: list[dict], seed: int) -> dict:
    digest = hashlib.sha256(f"{seed}:{record_key}".encode("utf-8")).hexdigest()
    slot = int(digest[:8], 16) % len(model_pool)
    return model_pool[slot]


def choose_reviewer_model(generator_model: dict, model_pool: list[dict]) -> dict:
    if len(model_pool) == 1:
        return model_pool[0]
    for candidate in model_pool:
        if candidate["alias"] != generator_model["alias"]:
            return candidate
    return model_pool[0]


def call_chat_completion(
    *,
    model_spec: dict,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    timeout_seconds: int,
) -> dict:
    url = model_spec["base_url"].rstrip("/") + "/v1/chat/completions"
    body = {
        "model": model_spec["model"],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {model_spec['api_key']}",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_message_content(response: dict) -> str:
    return response["choices"][0]["message"]["content"]


def probe_model(model_spec: dict, timeout_seconds: int) -> tuple[bool, str]:
    try:
        response = call_chat_completion(
            model_spec=model_spec,
            system_prompt="只输出 JSON：{\"ok\": true}",
            user_prompt="返回 {\"ok\": true}",
            temperature=0.0,
            timeout_seconds=timeout_seconds,
        )
        payload = json.loads(extract_message_content(response))
        if payload.get("ok") is True:
            return True, "ok"
        return False, f"unexpected_payload={payload}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def validate_record(record: dict) -> None:
    required_top = {"id", "source", "bucket", "split", "input", "output", "meta"}
    if set(record.keys()) != required_top:
        raise ValueError(f"{record.get('id')} top-level keys mismatch")
    input_required = {"history", "runtime_state", "active_task", "active_system_task", "paused_tasks", "focused_object", "user_message"}
    if set(record["input"].keys()) != input_required:
        raise ValueError(f"{record['id']} input keys mismatch")
    if set(record["output"].keys()) != ALLOWED_OUTPUT_KEYS:
        raise ValueError(f"{record['id']} output keys mismatch")
    if record["output"]["directive"] is not None and record["output"]["directive"].get("action") != "exit_runtime":
        raise ValueError(f"{record['id']} invalid directive action")
    task_payload = record["output"]["task"]
    if task_payload is not None:
        for command in task_payload.get("commands", []):
            if command.get("command") not in ALLOWED_TASK_COMMANDS:
                raise ValueError(f"{record['id']} invalid task command")
    track_count = sum(1 for value in record["output"].values() if value is not None)
    if track_count > 1:
        raise ValueError(f"{record['id']} has multiple active tracks")
    if record["bucket"] == "ambiguous_all_null" and track_count != 0:
        raise ValueError(f"{record['id']} ambiguous bucket must be all-null")
    if record["bucket"] == "directive_exit_runtime" and record["output"]["directive"] != {"action": "exit_runtime"}:
        raise ValueError(f"{record['id']} directive bucket mismatch")
    if record["bucket"] == "active_task_slot_fill":
        if not (record["input"]["active_task"] or record["input"]["active_system_task"]):
            raise ValueError(f"{record['id']} active_task_slot_fill missing active runtime")


def build_generation_prompt(anchor: dict, seed_brief: str, seen_user_messages: list[str]) -> str:
    task_commands = []
    if anchor["output"]["task"] is not None:
        task_commands = anchor["output"]["task"].get("commands", [])
    active_system_task = anchor["input"].get("active_system_task") or {}
    slot_target = ((active_system_task.get("slots") or {}).get("target_slot"))
    extra_guardrails: list[str] = []
    if anchor["bucket"] == "work_order_business_urge":
        extra_guardrails.append("用户要明确表达‘催一下/帮我催/能不能快点/尽快处理’这类催办诉求，但不要写成标签说明。")
    if anchor["bucket"] == "work_order_business_complaint":
        extra_guardrails.append("用户要明确表达投诉/不满升级/要求正式反馈的意思，不能只剩抱怨。")
    if anchor["bucket"] == "directive_exit_runtime":
        extra_guardrails.append("只表达结束当前话题，不要同时要求继续办理别的业务。")
    if anchor["bucket"] == "task_interrupt_resume_cancel":
        command_names = [command.get("command") for command in task_commands]
        if "cancel_flow" in command_names:
            extra_guardrails.append("这是取消当前 flow，不是退出整个上下文；不要写成‘换个话题’。")
        if any(command.get("command") == "resume_flow" for command in task_commands):
            extra_guardrails.append("这是继续刚才同一件事，用户要有‘接着来/继续办’的自然表达。")
        if any(command.get("command") == "start_flow" for command in task_commands):
            extra_guardrails.append("这是从当前方向切到另一个办理方向，用户要自然表达改主意。")
    if anchor["bucket"] == "active_task_slot_fill" and slot_target:
        extra_guardrails.append(f"当前只是在补 `{slot_target}` 对应的信息，user_message 应直接给内容本身。")
        if slot_target == "contact_phone":
            extra_guardrails.append("联系电话可以直接给数字，或‘打这个号’这种自然说法。")
        if slot_target == "complaint_confirm":
            extra_guardrails.append("确认语气要像真实口语，例如‘行，就这样提吧’。")
        if slot_target == "urge_reason":
            extra_guardrails.append("催办原因要藏在生活影响和着急里，不要写‘催办原因是’。")
        if slot_target == "complaint_reason":
            extra_guardrails.append("投诉原因要藏在抱怨和经历里，不要写‘投诉原因是’。")
    payload = {
        "anchor_id": anchor["id"],
        "bucket": anchor["bucket"],
        "split": anchor["split"],
        "seed_brief": seed_brief,
        "extra_guardrails": extra_guardrails,
        "focused_object_title": (anchor["input"].get("focused_object") or {}).get("title"),
        "focused_object_type": (anchor["input"].get("focused_object") or {}).get("type"),
        "input": anchor["input"],
        "output": anchor["output"],
        "meta": anchor["meta"],
        "seen_user_messages": seen_user_messages[-8:],
    }
    return (
        "请基于下面锚点样本，生成一条新的同 bucket 样本。\n"
        "要求：\n"
        "- output 不变，runtime 状态字段不变。\n"
        "- history 和 user_message 要像真实用户/客服对话。\n"
        "- 不要和 seen_user_messages 太相似。\n"
        "- history 轮数保持和锚点一致。\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def build_review_prompt(anchor: dict, candidate: dict, seen_user_messages: list[str]) -> str:
    payload = {
        "bucket": anchor["bucket"],
        "anchor_input": anchor["input"],
        "output": anchor["output"],
        "candidate": {
            "history": candidate["input"]["history"],
            "user_message": candidate["input"]["user_message"],
        },
        "focused_object": anchor["input"].get("focused_object"),
        "seen_user_messages": seen_user_messages[-12:],
    }
    return (
        "请审稿下面的候选样本，判断它是否自然、无模板腔、无系统术语、无自我标注，并且仍然支持原 output。\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def normalize_generated_fields(anchor: dict, generated_fields: dict, record_id: str, model_alias: str, reviewer_alias: str) -> dict:
    rewritten = json.loads(json.dumps(anchor, ensure_ascii=False))
    rewritten["id"] = record_id
    rewritten["source"] = "llm-augmented"
    rewritten["input"]["history"] = generated_fields["history"]
    rewritten["input"]["user_message"] = generated_fields["user_message"]
    rewritten["meta"] = {
        "primary_track": anchor["meta"].get("primary_track"),
        "notes": anchor["meta"].get("notes"),
        "long_context": anchor["meta"].get("long_context", len(anchor["input"]["history"]) >= 4),
    }
    rewritten["meta"]["source_anchor_id"] = anchor["id"]
    rewritten["meta"]["generation_model_alias"] = model_alias
    rewritten["meta"]["review_model_alias"] = reviewer_alias
    rewritten["meta"]["generation_notes"] = generated_fields.get("generation_notes", [])
    return rewritten


def contains_banned_language(text: str) -> bool:
    return any(pattern in text for pattern in BANNED_PATTERNS)


def contains_suspicious_language(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in SUSPICIOUS_PATTERNS)


def heuristic_check(record: dict, seen_user_messages: set[str]) -> list[str]:
    issues: list[str] = []
    user_message = record["input"]["user_message"].strip()
    if not user_message:
        issues.append("empty user_message")
    if user_message in seen_user_messages:
        issues.append("duplicate user_message")
    if contains_banned_language(user_message):
        issues.append("banned pattern in user_message")
    if contains_suspicious_language(user_message):
        issues.append("suspicious pattern in user_message")
    for turn in record["input"]["history"]:
        text = turn["text"].strip()
        if not text:
            issues.append("empty history text")
            continue
        if contains_banned_language(text):
            issues.append("banned pattern in history")
        if "比如" in text and len(text) > 18:
            issues.append("template-like history phrase")
    if record["bucket"] == "directive_exit_runtime":
        if any(word in user_message for word in ["投诉", "催办", "提交"]) and any(word in user_message for word in ["换个话题", "先不聊", "先放一放", "先这样"]):
            pass
    if record["bucket"] == "work_order_business_urge":
        if not any(word in user_message for word in ["催", "快点", "尽快", "抓紧", "加急"]):
            issues.append("urge bucket missing explicit urge cue")
    if record["bucket"] == "work_order_business_complaint":
        if not any(word in user_message for word in ["投诉", "说法", "反馈", "处理结果", "太过分"]):
            issues.append("complaint bucket missing complaint cue")
    return issues


def sample_seed_brief(bucket: str, index: int) -> str:
    briefs = {
        "ambiguous_all_null": [
            "用户只是笼统求助，提到门牌、门锁、显示名称之类，但仍不足以唯一落到某个 flow。",
            "用户说得含糊，像在求处理，但没有说清是改名、重置还是补办。",
            "用户在催你帮他弄一下某件事，但信息仍然不够具体。",
        ],
        "active_task_slot_fill": [
            "用户只补当前槽位内容，可以很短，也可以带情绪，但不解释自己在补槽。",
            "用户延续当前流程，只说补充原因、电话、确认或项目名本身。",
            "像真实追问中的半句补充，重点是自然口语。",
        ],
        "task_interrupt_resume_cancel": [
            "用户在继续刚才的事、取消当前流程，或从催办改成投诉，语气自然一点。",
            "用户改主意，但不会说 resume/cancel 这些系统词。",
            "像真实多轮客服里临时换想法的说法。",
        ],
        "directive_exit_runtime": [
            "用户想结束当前话题，简短、自然，不重复说两遍。",
            "像‘先这样吧’‘这个先不聊了’这种结束语。",
            "用户收住当前上下文，但不是取消业务协议细节。",
        ],
        "work_order_business_urge": [
            "用户想催办，着急和原因藏在抱怨里，不要总是‘原因是’。",
            "像真实住户催师傅快点，不直接解释标签。",
            "用户催办时会夹带生活影响和着急情绪。",
        ],
        "work_order_business_complaint": [
            "用户想投诉，不满情绪和原因藏在自然表达里。",
            "像真实住户说反复拖延、上门爽约、问题没解决。",
            "允许用户说‘直接投诉吧’，但别写成标注话术。",
        ],
    }
    choices = briefs[bucket]
    return choices[index % len(choices)]


def next_record_id(bucket: str, split: str, index: int) -> str:
    return f"tp_r3_{bucket}_{split}_{index:03d}"


def compute_bucket_counts(rows: list[dict]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {
        bucket: {"train": 0, "val": 0}
        for bucket in TARGET_BUCKETS
    }
    for row in rows:
        counts[row["bucket"]][row["split"]] += 1
    return counts


def build_summary(dataset_id: str, rows: list[dict], health_report: list[dict]) -> str:
    counts = compute_bucket_counts(rows)
    lines = [
        f"# {dataset_id} Summary",
        "",
        "- source base: `reduced_round03_base_v1`",
        "- purpose: reduced `round_03` augmented dataset for focused SFT retry",
        "",
        "| bucket | train_actual | train_target | val_actual | val_target |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for bucket, target in TARGET_BUCKETS.items():
        actual = counts[bucket]
        lines.append(
            f"| `{bucket}` | {actual['train']} | {target['train']} | {actual['val']} | {target['val']} |"
        )
    lines.extend(
        [
            "",
            f"- total_records: `{len(rows)}`",
            f"- train_total: `{sum(item['train'] for item in counts.values())}`",
            f"- val_total: `{sum(item['val'] for item in counts.values())}`",
            "",
            "## Model Health",
            "",
        ]
    )
    for item in health_report:
        lines.append(f"- `{item['alias']}` / `{item['model']}`: `{item['detail']}`")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Augment reduced round_03 TurnPlan dataset with targeted LLM generation.")
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--temperature", type=float, default=0.9)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument("--seed", type=int, default=20260607)
    parser.add_argument("--limit-per-split", type=int, default=None, help="Optional debug limit on new generations per split.")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def generate_candidate(
    *,
    anchor: dict,
    record_id: str,
    model_pool: list[dict],
    seen_user_messages: list[str],
    temperature: float,
    timeout_seconds: int,
    max_attempts: int,
    retry_delay_seconds: float,
    seed_brief: str,
    seed: int,
) -> dict:
    generator_model = choose_model(record_id, model_pool, seed)
    reviewer_model = choose_reviewer_model(generator_model, model_pool)
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            generation_response = call_chat_completion(
                model_spec=generator_model,
                system_prompt=GENERATION_SYSTEM_PROMPT,
                user_prompt=build_generation_prompt(anchor, seed_brief, seen_user_messages),
                temperature=temperature,
                timeout_seconds=timeout_seconds,
            )
            generated_fields = json.loads(extract_message_content(generation_response))
            candidate = normalize_generated_fields(
                anchor,
                generated_fields,
                record_id,
                generator_model["alias"],
                reviewer_model["alias"],
            )
            validate_record(candidate)
            heuristic_issues = heuristic_check(candidate, set(seen_user_messages))
            if heuristic_issues:
                raise ValueError("; ".join(heuristic_issues))
            review_response = call_chat_completion(
                model_spec=reviewer_model,
                system_prompt=REVIEW_SYSTEM_PROMPT,
                user_prompt=build_review_prompt(anchor, candidate, seen_user_messages),
                temperature=0.0,
                timeout_seconds=timeout_seconds,
            )
            review_payload = json.loads(extract_message_content(review_response))
            if not review_payload.get("pass"):
                raise ValueError("review_rejected: " + " | ".join(review_payload.get("issues", [])))
            return candidate
        except (ValueError, error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            time.sleep(retry_delay_seconds)
    raise RuntimeError(f"failed to generate {record_id}: {last_error}") from last_error


def main() -> None:
    args = parse_args()
    base_train = read_jsonl(args.input_dir / "records_train.jsonl")
    base_val = read_jsonl(args.input_dir / "records_val.jsonl")
    base_rows = base_train + base_val
    for row in base_rows:
        validate_record(row)

    model_pool = default_model_pool()
    if not model_pool:
        raise RuntimeError("No model pool available. Provide TURNPLAN_LLM_API_KEY and keep project DeepSeek config accessible.")

    healthy_pool: list[dict] = []
    health_report: list[dict] = []
    for model_spec in model_pool:
        ok, detail = probe_model(model_spec, min(args.timeout_seconds, 45))
        health_report.append(
            {
                "alias": model_spec["alias"],
                "model": model_spec["model"],
                "base_url": model_spec["base_url"],
                "ok": ok,
                "detail": detail,
            }
        )
        if ok:
            healthy_pool.append(model_spec)
    if not healthy_pool:
        raise RuntimeError(f"No healthy models available: {health_report}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.overwrite:
        for path in [args.output_dir / "records_train.jsonl", args.output_dir / "records_val.jsonl", args.output_dir / "manifest.json", args.output_dir / "summary.md", args.output_dir / "progress.json"]:
            if path.exists():
                path.unlink()

    train_output = read_jsonl(args.output_dir / "records_train.jsonl")
    val_output = read_jsonl(args.output_dir / "records_val.jsonl")
    if not train_output and not val_output:
        train_output = json.loads(json.dumps(base_train, ensure_ascii=False))
        val_output = json.loads(json.dumps(base_val, ensure_ascii=False))
        write_jsonl(args.output_dir / "records_train.jsonl", train_output)
        write_jsonl(args.output_dir / "records_val.jsonl", val_output)

    all_rows = train_output + val_output
    existing_ids = {row["id"] for row in all_rows}
    seen_user_messages_by_split = {
        "train": [row["input"]["user_message"] for row in train_output],
        "val": [row["input"]["user_message"] for row in val_output],
    }

    rng = random.Random(args.seed)
    progress: list[dict] = []

    for split, output_rows, base_rows_for_split in [
        ("train", train_output, base_train),
        ("val", val_output, base_val),
    ]:
        current_counts = Counter(row["bucket"] for row in output_rows)
        base_by_bucket: dict[str, list[dict]] = {}
        for row in base_rows_for_split:
            base_by_bucket.setdefault(row["bucket"], []).append(row)
        for bucket, target in TARGET_BUCKETS.items():
            needed = target[split] - current_counts.get(bucket, 0)
            if args.limit_per_split is not None:
                needed = min(needed, args.limit_per_split)
            if needed <= 0:
                continue
            anchors = base_by_bucket[bucket][:]
            rng.shuffle(anchors)
            anchor_index = 0
            generated_for_bucket = 0
            while generated_for_bucket < needed:
                if not anchors:
                    raise RuntimeError(f"No anchors available for bucket {bucket} / {split}")
                anchor = anchors[anchor_index % len(anchors)]
                record_index = target[split] - needed + generated_for_bucket
                record_id = next_record_id(bucket, split, record_index)
                if record_id in existing_ids:
                    generated_for_bucket += 1
                    anchor_index += 1
                    continue
                seed_brief = sample_seed_brief(bucket, generated_for_bucket)
                candidate = generate_candidate(
                    anchor=anchor,
                    record_id=record_id,
                    model_pool=healthy_pool,
                    seen_user_messages=seen_user_messages_by_split[split],
                    temperature=args.temperature,
                    timeout_seconds=args.timeout_seconds,
                    max_attempts=args.max_attempts,
                    retry_delay_seconds=args.retry_delay_seconds,
                    seed_brief=seed_brief,
                    seed=args.seed,
                )
                output_rows.append(candidate)
                existing_ids.add(candidate["id"])
                seen_user_messages_by_split[split].append(candidate["input"]["user_message"])
                progress.append(
                    {
                        "id": candidate["id"],
                        "split": split,
                        "bucket": bucket,
                        "anchor_id": anchor["id"],
                        "generation_model_alias": candidate["meta"]["generation_model_alias"],
                        "review_model_alias": candidate["meta"]["review_model_alias"],
                    }
                )
                write_jsonl(args.output_dir / "records_train.jsonl", train_output)
                write_jsonl(args.output_dir / "records_val.jsonl", val_output)
                (args.output_dir / "progress.json").write_text(
                    json.dumps(progress, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                print(
                    json.dumps(
                        {
                            "status": "generated",
                            "split": split,
                            "bucket": bucket,
                            "id": candidate["id"],
                            "anchor_id": anchor["id"],
                            "model": candidate["meta"]["generation_model_alias"],
                        },
                        ensure_ascii=False,
                    )
                )
                generated_for_bucket += 1
                anchor_index += 1

    final_train = read_jsonl(args.output_dir / "records_train.jsonl")
    final_val = read_jsonl(args.output_dir / "records_val.jsonl")
    final_rows = final_train + final_val
    for row in final_rows:
        validate_record(row)

    manifest = {
        "dataset_id": args.output_dir.name,
        "source_dataset": args.input_dir.name,
        "target_buckets": TARGET_BUCKETS,
        "train_total": len(final_train),
        "val_total": len(final_val),
        "bucket_counts": compute_bucket_counts(final_rows),
        "health_report": health_report,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (args.output_dir / "summary.md").write_text(
        build_summary(args.output_dir.name, final_rows, health_report),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "output_dir": str(args.output_dir),
                "train_total": len(final_train),
                "val_total": len(final_val),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
