from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import time
from copy import deepcopy
from pathlib import Path
from urllib import error, request

from dataset_contract import CANONICAL_DIR
from validate_dataset import validate_record


DEFAULT_OPENAI_BASE_URL = "https://jsyai.xinglian.work"
DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"
DEFAULT_TRAIN_INPUT = CANONICAL_DIR / "records_train.jsonl"
DEFAULT_VAL_INPUT = CANONICAL_DIR / "records_val.jsonl"
DEFAULT_OUTPUT_DIR = CANONICAL_DIR.parent / "canonical_llm"
PROJECT_ENV_PATH = Path(__file__).resolve().parents[4] / "customer-service-backend" / ".env"

BANNED_USER_PHRASES = [
    "这是投诉原因补充",
    "我是在补催办原因",
    "我在补催办原因",
    "我在确认具体服务项目",
    "我是在补联系电话",
    "这轮我只是咨询",
    "别默认进入办理",
    "先按规则说明来",
    "围绕这个规则本身",
    "顺着刚才的话题再补充一下",
    "按这单本身回答就行",
    "别串到别的工单",
]

SUSPICIOUS_USER_PHRASES = [
    "比如帮我",
    "原因就是",
    "投诉原因就是",
    "催办原因是",
    "我想换个话题，我想换个话题",
]

REWRITE_SYSTEM_PROMPT = """你是“物业客服 TurnPlan 训练样本自然化重写器”。

你的任务不是改标签，而是只改写对话文本，让训练样本更像真实中文用户和真实客服对话。

这是一轮“替换式重写”，不是“原句保留后做同义替换”。如果原句带有模板拼接痕迹、标注痕迹、系统提示腔或脚本腔，你要整句换成真实人会说的话。

你必须遵守：
1. 绝对不能修改结构化状态字段：runtime_state / active_task / active_system_task / paused_tasks / focused_object 都不能改。
2. 绝对不能修改 output 标签。
3. 只允许改写：
   - input.history 中每一条 text
   - input.user_message
4. 改写后要保持这条样本原本想表达的语义和标签仍然成立。
5. 输出必须是合法 JSON，只返回：
   {
     "history": [{"role": "...", "text": "..."}],
     "user_message": "...",
     "rewrite_notes": ["..."]
   }

高优先级要求：
1. 禁止模板拼接腔：
   - 不要出现“这个你帮我处理一下，比如帮我改门牌显示名称”这种半成品句子。
   - 如果原句是这类拼接痕迹，直接换成像“我想把门牌名字改一下”这样完整自然的话。
2. 禁止意图自我标注：
   - 不要出现“这是投诉原因补充”“我在补催办原因”“我在确认具体服务项目”。
   - 用户不会解释自己正在执行什么标签动作，只会直接说内容本身。
3. slot 值要藏在真实表达里：
   - 用户补 complaint_reason / urge_reason 时，不必总说“原因是”。
   - 更自然的说法可能是“已经等了三天了还没人来”“门禁一直刷不开，进出都受影响了”“你记这个电话就行”。
4. 允许自然模糊：
   - 不要默认用户每句话都清楚、准确、完整。
   - 对 all_null、上下文追问、半句补充，可以保留自然的模糊、省略、情绪表达，只要不改变原标签。
5. history 也要自然：
   - assistant 不要总是“好的/明白/可以”三板斧。
   - user 和 assistant 要像在接着上一句说，而不是模板问答。

反例与正例：
1. 模板拼接反例：
   - “那你先看着办吧，比如帮我改门牌显示名称”
   - 更自然：“门牌名字这边想改一下”
2. 自我标注反例：
   - “我不满意主要因为预约时间一拖再拖，这是投诉原因补充”
   - 更自然：“之前说今天来，结果一拖再拖，我这边确实挺不满意的”
3. 催办原因反例：
   - “催办原因是门禁刷不开很耽误事，我是在补催办原因”
   - 更自然：“门禁一直刷不开，家里进出都受影响了”
4. 追问反例：
   - “围绕这个规则本身，关于装修报备，你顺着刚才的话题再补充一下，别只给结论”
   - 更自然：“那装修报备这块具体怎么弄”

按 bucket 的额外约束：
- chitchat：更像单句闲聊，不要永远“打招呼 + 追问”复合句。
- directive_exit_runtime：短一点、自然一点，例如“算了先不弄这个了”“换个话题吧”。
- work_order_read_only_task：只保留真实查询诉求，不要带系统内部视角后缀。
- service_item_knowledge：直接咨询，不要写成控制系统行为的命令。
- object_context_followup：像真实追问，例如“多说一点”“那具体怎么算”“什么意思”。
- active_task_slot_fill：用户只说补充内容，不要解释自己在补槽。
- urge / complaint / interrupt：用户表达情况、着急、不满或改主意，不要写成显式流程指令。

质量底线：
- 保留原有对象指向，不要把当前工单或服务项目说丢。
- 如果样本依赖 active_task / active_system_task 才成立，改写后仍然要像是在当前上下文里继续说。
- 不要生成新的业务事实，不要新增原样本没有的信息。
"""

REVIEW_SYSTEM_PROMPT = """你是“物业客服 TurnPlan 样本自然性审稿人”。

你会收到：
1. 原始样本（标签和状态字段不可变）
2. 重写后的 history + user_message

你要判断重写后的语言层是否真的像真实用户/客服，而不是模板、脚本或标注腔。

重点检查：
1. 有没有模板拼接痕迹，例如“比如帮我…”、“A，我想换个话题，B，我想换个话题”。
2. 有没有意图自我标注，例如“这是投诉原因补充”“我在补催办原因”“我在确认具体服务项目”。
3. 有没有系统内部视角，例如“别串到别的工单”“按这单本身回答就行”“别默认进入办理”。
4. 用户的话是否自然，是否像真实口语，而不是为了帮助分类器故意说清楚所有标签。
5. 是否保持了原标签仍然成立，没有改掉语义。

只输出合法 JSON：
{
  "pass": true,
  "issues": [],
  "advice": []
}
"""


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {row["id"] for row in read_jsonl(path)}


def write_progress(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def dedupe_output_file(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"rows": 0, "unique_ids": 0, "removed_duplicates": 0}
    rows = read_jsonl(path)
    deduped_by_id: dict[str, dict] = {}
    order: list[str] = []
    for row in rows:
        record_id = row["id"]
        if record_id not in deduped_by_id:
            order.append(record_id)
        deduped_by_id[record_id] = row
    deduped_rows = [deduped_by_id[record_id] for record_id in order]
    removed_duplicates = len(rows) - len(deduped_rows)
    if removed_duplicates > 0:
        write_jsonl(path, deduped_rows)
    return {
        "rows": len(rows),
        "unique_ids": len(deduped_rows),
        "removed_duplicates": removed_duplicates,
    }


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


def parse_model_pool(raw_json: str | None) -> list[dict]:
    if not raw_json:
        return default_model_pool()
    payload = json.loads(raw_json)
    if not isinstance(payload, list):
        raise ValueError("model pool must be a JSON list")
    normalized = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"model pool item {index} must be an object")
        for key in ("alias", "model", "base_url", "api_key"):
            if not item.get(key):
                raise ValueError(f"model pool item {index} missing {key}")
        normalized.append(
            {
                "alias": str(item["alias"]),
                "model": str(item["model"]),
                "base_url": str(item["base_url"]),
                "api_key": str(item["api_key"]),
            }
        )
    return normalized


def choose_model(record_id: str, model_pool: list[dict], strategy: str, seed: int) -> dict:
    if len(model_pool) == 1:
        return model_pool[0]
    if strategy == "round_robin":
        digest = hashlib.sha256(record_id.encode("utf-8")).hexdigest()
        slot = int(digest[:8], 16) % len(model_pool)
        return model_pool[slot]
    rng = random.Random(f"{seed}:{record_id}")
    return model_pool[rng.randrange(len(model_pool))]


def ordered_models_for_record(record_id: str, model_pool: list[dict], strategy: str, seed: int) -> list[dict]:
    if len(model_pool) <= 1:
        return model_pool[:]
    chosen = choose_model(record_id, model_pool, strategy, seed)
    ordered = [chosen]
    ordered.extend(item for item in model_pool if item["alias"] != chosen["alias"])
    return ordered


def choose_reviewer_model(rewrite_model: dict, model_pool: list[dict]) -> dict:
    if len(model_pool) == 1:
        return model_pool[0]
    for candidate in model_pool:
        if candidate["alias"] != rewrite_model["alias"]:
            return candidate
    return model_pool[0]


def bucket_rewrite_hint(record: dict) -> str:
    bucket = record["bucket"]
    if bucket == "ambiguous_all_null":
        return "让用户说得自然模糊、不完整，但仍然不足以唯一确定 flow 或 knowledge intent。"
    if bucket == "directive_exit_runtime":
        return "让用户像自然结束当前话题，不要重复表达同一个退出目的。"
    if bucket == "active_task_slot_fill":
        return "让用户直接说补充内容本身，不要解释自己在补什么。"
    if bucket == "task_interrupt_resume_cancel":
        return "让用户像真实对话那样改主意、打断、恢复，不要显式说 resume/cancel/switch。"
    if bucket == "work_order_read_only_task":
        return "让用户像正常查状态、查列表、查详情，不要带系统内部视角。"
    if bucket == "service_item_knowledge":
        return "让用户像真实咨询规则或服务说明，不要像在控制系统行为。"
    if bucket == "object_context_followup":
        return "让用户像顺着上一轮继续追问，不要像写提示词。"
    if bucket in {"work_order_business_urge", "work_order_business_complaint"}:
        return "让用户通过抱怨、着急、补充情况来表达，而不是显式说“原因是……”。"
    if bucket == "chitchat":
        return "更像真实的单句寒暄、试探、闲聊，不要总是复合句。"
    return "保持真实口语感。"


def build_rewrite_prompt(record: dict) -> str:
    payload = {
        "id": record["id"],
        "bucket": record["bucket"],
        "split": record["split"],
        "input": record["input"],
        "output": record["output"],
        "meta": record["meta"],
    }
    return (
        "请重写下面这条样本中的 history 与 user_message。\n"
        "注意：这是替换式重写，不是在原句上小修小补。不要改 output，也不要改 runtime_state / active_task / active_system_task / paused_tasks / focused_object。\n"
        f"这条样本的专项提醒：{bucket_rewrite_hint(record)}\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def build_review_prompt(original_record: dict, rewritten_record: dict) -> str:
    payload = {
        "original": {
            "id": original_record["id"],
            "bucket": original_record["bucket"],
            "input": original_record["input"],
            "output": original_record["output"],
        },
        "rewritten": {
            "history": rewritten_record["input"]["history"],
            "user_message": rewritten_record["input"]["user_message"],
        },
    }
    return (
        "请审稿这条重写后的样本。\n"
        "如果语言仍然像模板、像标签提示、像系统视角，或者改坏了原标签语义，就判定为不通过。\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


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


def probe_model(model_spec: dict, timeout_seconds: int) -> tuple[bool, str]:
    try:
        payload = call_chat_completion(
            model_spec=model_spec,
            system_prompt='只返回 JSON：{"pong": true}',
            user_prompt="ping",
            temperature=0,
            timeout_seconds=timeout_seconds,
        )
        content = extract_json_content(payload)
        if content.get("pong") is True:
            return True, "ok"
        return False, f"unexpected payload: {content}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def extract_json_content(payload: dict) -> dict:
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise ValueError(f"Unexpected LLM response payload: {payload}") from exc
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        content = "".join(text_parts)
    if not isinstance(content, str):
        raise ValueError(f"Unexpected LLM content type: {type(content)!r}")
    return json.loads(content)


def validate_rewrite_shape(rewrite: dict, record: dict) -> None:
    if set(rewrite.keys()) != {"history", "user_message", "rewrite_notes"}:
        raise ValueError(f"{record['id']} rewrite keys mismatch: {rewrite.keys()}")
    if not isinstance(rewrite["history"], list):
        raise ValueError(f"{record['id']} rewrite history must be a list")
    if not isinstance(rewrite["user_message"], str) or not rewrite["user_message"].strip():
        raise ValueError(f"{record['id']} rewrite user_message must be non-empty")
    if not isinstance(rewrite["rewrite_notes"], list):
        raise ValueError(f"{record['id']} rewrite_notes must be a list")
    source_history = record["input"]["history"]
    if len(rewrite["history"]) != len(source_history):
        raise ValueError(f"{record['id']} history length changed")
    for index, turn in enumerate(rewrite["history"]):
        if set(turn.keys()) != {"role", "text"}:
            raise ValueError(f"{record['id']} history item {index} keys mismatch")
        if turn["role"] != source_history[index]["role"]:
            raise ValueError(f"{record['id']} history item {index} role changed")
        if not isinstance(turn["text"], str) or not turn["text"].strip():
            raise ValueError(f"{record['id']} history item {index} text must be non-empty")


def heuristic_quality_gate(rewritten_record: dict) -> None:
    texts = [turn["text"] for turn in rewritten_record["input"]["history"]]
    texts.append(rewritten_record["input"]["user_message"])
    full_text = "\n".join(texts)
    for phrase in BANNED_USER_PHRASES:
        if phrase in full_text:
            raise ValueError(f"suspicious phrase detected: {phrase}")
    for phrase in SUSPICIOUS_USER_PHRASES:
        if phrase in full_text:
            raise ValueError(f"template-like phrase detected: {phrase}")
    if full_text.count("我想换个话题") > 1:
        raise ValueError("repeated exit purpose detected")


def validate_review_shape(review: dict, record_id: str) -> None:
    if set(review.keys()) != {"pass", "issues", "advice"}:
        raise ValueError(f"{record_id} review keys mismatch")
    if not isinstance(review["pass"], bool):
        raise ValueError(f"{record_id} review pass must be bool")
    if not isinstance(review["issues"], list) or not isinstance(review["advice"], list):
        raise ValueError(f"{record_id} review issues/advice must be lists")


def build_rewritten_record(record: dict, rewrite: dict, rewrite_model: dict, reviewer_model: dict) -> dict:
    rewritten = deepcopy(record)
    rewritten["input"]["history"] = rewrite["history"]
    rewritten["input"]["user_message"] = rewrite["user_message"]
    rewritten["source"] = "llm-rewritten"
    rewritten["meta"] = deepcopy(record["meta"])
    rewritten["meta"]["rewrite_model"] = rewrite_model["model"]
    rewritten["meta"]["rewrite_model_alias"] = rewrite_model["alias"]
    rewritten["meta"]["review_model"] = reviewer_model["model"]
    rewritten["meta"]["review_model_alias"] = reviewer_model["alias"]
    rewritten["meta"]["rewrite_notes"] = rewrite["rewrite_notes"]
    return rewritten


def rewrite_record(
    *,
    record: dict,
    rewrite_model: dict,
    reviewer_models: list[dict],
    temperature: float,
    timeout_seconds: int,
    max_attempts: int,
    retry_delay_seconds: float,
) -> dict:
    rewrite_prompt = build_rewrite_prompt(record)
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            rewrite_payload = call_chat_completion(
                model_spec=rewrite_model,
                system_prompt=REWRITE_SYSTEM_PROMPT,
                user_prompt=rewrite_prompt,
                temperature=temperature,
                timeout_seconds=timeout_seconds,
            )
            rewrite = extract_json_content(rewrite_payload)
            validate_rewrite_shape(rewrite, record)
            reviewer_errors: list[str] = []
            review_passed = False
            rewritten = None
            for reviewer_model in reviewer_models:
                rewritten_candidate = build_rewritten_record(record, rewrite, rewrite_model, reviewer_model)
                validate_record(rewritten_candidate)
                heuristic_quality_gate(rewritten_candidate)
                try:
                    review_prompt = build_review_prompt(record, rewritten_candidate)
                    review_payload = call_chat_completion(
                        model_spec=reviewer_model,
                        system_prompt=REVIEW_SYSTEM_PROMPT,
                        user_prompt=review_prompt,
                        temperature=0.2,
                        timeout_seconds=timeout_seconds,
                    )
                    review = extract_json_content(review_payload)
                    validate_review_shape(review, record["id"])
                    if not review["pass"]:
                        issues = "; ".join(review["issues"]) or "review model rejected rewrite"
                        reviewer_errors.append(f"{reviewer_model['alias']}: {issues}")
                        continue
                    rewritten_candidate["meta"]["review_issues"] = review["issues"]
                    rewritten_candidate["meta"]["review_advice"] = review["advice"]
                    rewritten = rewritten_candidate
                    review_passed = True
                    break
                except (ValueError, error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
                    reviewer_errors.append(f"{reviewer_model['alias']}: {exc}")
                    continue
            if not review_passed or rewritten is None:
                raise ValueError(f"all reviewers failed: {' | '.join(reviewer_errors)}")
            validate_record(rewritten)
            return rewritten
        except (ValueError, error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            time.sleep(retry_delay_seconds)
    raise RuntimeError(f"Failed to rewrite {record['id']}: {last_error}") from last_error


def rewrite_records(
    *,
    records: list[dict],
    output_path: Path,
    progress_path: Path,
    model_pool: list[dict],
    strategy: str,
    routing_seed: int,
    temperature: float,
    timeout_seconds: int,
    max_attempts: int,
    retry_delay_seconds: float,
    limit: int | None,
    start_index: int,
) -> dict:
    selected = records[start_index:]
    if limit is not None:
        selected = selected[:limit]
    dedupe_stats = dedupe_output_file(output_path)
    if dedupe_stats["removed_duplicates"] > 0:
        print(json.dumps({"status": "deduped_existing_output", "output_path": str(output_path), **dedupe_stats}, ensure_ascii=False))
    existing_ids = read_existing_ids(output_path)
    pending_records = [record for record in selected if record["id"] not in existing_ids]
    if pending_records:
        print(
            json.dumps(
                {
                    "status": "resume",
                    "output_path": str(output_path),
                    "existing": len(existing_ids),
                    "pending": len(pending_records),
                    "selected": len(selected),
                },
                ensure_ascii=False,
            )
        )
    else:
        print(
            json.dumps(
                {
                    "status": "resume",
                    "output_path": str(output_path),
                    "existing": len(existing_ids),
                    "pending": 0,
                    "selected": len(selected),
                },
                ensure_ascii=False,
            )
        )

    progress = {
        "output_path": str(output_path),
        "selected_records": len(selected),
        "completed_records": len(existing_ids.intersection({record["id"] for record in selected})),
        "pending_records": len(pending_records),
        "last_completed_id": None,
    }
    write_progress(progress_path, progress)

    completed_count = progress["completed_records"]
    total_selected = len(selected)
    for record in pending_records:
        rewrite_candidates = ordered_models_for_record(record["id"], model_pool, strategy, routing_seed)
        rewritten = None
        last_error: Exception | None = None
        rewrite_model = None
        reviewer_models: list[dict] = []
        for rewrite_model_candidate in rewrite_candidates:
            reviewer_models_candidate = [choose_reviewer_model(rewrite_model_candidate, model_pool)]
            reviewer_models_candidate.extend(
                item
                for item in model_pool
                if item["alias"] not in {reviewer_models_candidate[0]["alias"], rewrite_model_candidate["alias"]}
            )
            if rewrite_model_candidate["alias"] not in {item["alias"] for item in reviewer_models_candidate}:
                reviewer_models_candidate.append(rewrite_model_candidate)
            try:
                rewritten = rewrite_record(
                    record=record,
                    rewrite_model=rewrite_model_candidate,
                    reviewer_models=reviewer_models_candidate,
                    temperature=temperature,
                    timeout_seconds=timeout_seconds,
                    max_attempts=max_attempts,
                    retry_delay_seconds=retry_delay_seconds,
                )
                rewrite_model = rewrite_model_candidate
                reviewer_models = reviewer_models_candidate
                break
            except RuntimeError as exc:
                last_error = exc
                continue
        if rewritten is None or rewrite_model is None:
            raise RuntimeError(f"Failed to rewrite {record['id']} with all models: {last_error}") from last_error
        append_jsonl(output_path, rewritten)
        completed_count += 1
        progress = {
            "output_path": str(output_path),
            "selected_records": total_selected,
            "completed_records": completed_count,
            "pending_records": total_selected - completed_count,
            "last_completed_id": record["id"],
        }
        write_progress(progress_path, progress)
        print(
            json.dumps(
                {
                    "status": "rewritten",
                    "id": record["id"],
                    "progress": f"{completed_count}/{total_selected}",
                    "rewrite_model": rewrite_model["alias"],
                    "review_model": rewritten["meta"]["review_model_alias"],
                },
                ensure_ascii=False,
            )
        )
    final_records = read_jsonl(output_path)
    final_ids = {record["id"] for record in selected}
    kept_records = [row for row in final_records if row["id"] in final_ids]
    if len(kept_records) != total_selected:
        raise RuntimeError(f"Output count mismatch for {output_path}: {len(kept_records)} != {total_selected}")
    if {row["id"] for row in kept_records} != final_ids:
        raise RuntimeError(f"Output ids mismatch for {output_path}")
    write_progress(
        progress_path,
        {
            "output_path": str(output_path),
            "selected_records": total_selected,
            "completed_records": total_selected,
            "pending_records": 0,
            "last_completed_id": kept_records[-1]["id"] if kept_records else None,
        },
    )
    return {"count": len(kept_records), "output_path": str(output_path)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rewrite TurnPlan dataset utterances with multiple LLMs.")
    parser.add_argument("--train-input", type=Path, default=DEFAULT_TRAIN_INPUT)
    parser.add_argument("--val-input", type=Path, default=DEFAULT_VAL_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model-pool-json", default=os.environ.get("TURNPLAN_MODEL_POOL_JSON"))
    parser.add_argument("--model-strategy", choices=["round_robin", "random_seed"], default="round_robin")
    parser.add_argument("--routing-seed", type=int, default=20260606)
    parser.add_argument("--temperature", type=float, default=0.9)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument("--limit", type=int, default=None, help="Optional per-split limit for a small trial run.")
    parser.add_argument("--start-index", type=int, default=0, help="Optional per-split start index for resume.")
    parser.add_argument("--split", choices=["train", "val", "both"], default="both")
    parser.add_argument("--overwrite", action="store_true", help="Delete existing rewritten output files before running.")
    args = parser.parse_args()
    args.model_pool = parse_model_pool(args.model_pool_json)
    if not args.model_pool:
        parser.error("No available model pool. Provide TURNPLAN_LLM_API_KEY or --model-pool-json, and ensure project DeepSeek config exists.")
    return args


def main() -> None:
    args = parse_args()
    healthy_pool = []
    health_report = []
    for model_spec in args.model_pool:
        ok, detail = probe_model(model_spec, min(args.timeout_seconds, 45))
        health_report.append({"alias": model_spec["alias"], "model": model_spec["model"], "base_url": model_spec["base_url"], "ok": ok, "detail": detail})
        if ok:
            healthy_pool.append(model_spec)
    if not healthy_pool:
        raise RuntimeError(f"No healthy models available: {health_report}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "model_pool": [
            {"alias": item["alias"], "model": item["model"], "base_url": item["base_url"]}
            for item in healthy_pool
        ],
        "model_health": health_report,
    }

    if args.overwrite:
        for path in (
            args.output_dir / "records_train.jsonl",
            args.output_dir / "records_val.jsonl",
            args.output_dir / "progress_train.json",
            args.output_dir / "progress_val.json",
        ):
            if path.exists():
                path.unlink()

    if args.split in {"train", "both"}:
        train_records = read_jsonl(args.train_input)
        rewritten_train = rewrite_records(
            records=train_records,
            output_path=args.output_dir / "records_train.jsonl",
            progress_path=args.output_dir / "progress_train.json",
            model_pool=healthy_pool,
            strategy=args.model_strategy,
            routing_seed=args.routing_seed,
            temperature=args.temperature,
            timeout_seconds=args.timeout_seconds,
            max_attempts=args.max_attempts,
            retry_delay_seconds=args.retry_delay_seconds,
            limit=args.limit,
            start_index=args.start_index,
        )
        summary["train"] = rewritten_train["count"]

    if args.split in {"val", "both"}:
        val_records = read_jsonl(args.val_input)
        rewritten_val = rewrite_records(
            records=val_records,
            output_path=args.output_dir / "records_val.jsonl",
            progress_path=args.output_dir / "progress_val.json",
            model_pool=healthy_pool,
            strategy=args.model_strategy,
            routing_seed=args.routing_seed,
            temperature=args.temperature,
            timeout_seconds=args.timeout_seconds,
            max_attempts=args.max_attempts,
            retry_delay_seconds=args.retry_delay_seconds,
            limit=args.limit,
            start_index=args.start_index,
        )
        summary["val"] = rewritten_val["count"]

    (args.output_dir / "rewrite_config.json").write_text(
        json.dumps(
            {
                "split": args.split,
                "limit": args.limit,
                "start_index": args.start_index,
                "model_strategy": args.model_strategy,
                "routing_seed": args.routing_seed,
                "temperature": args.temperature,
                "timeout_seconds": args.timeout_seconds,
                "model_pool": summary["model_pool"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": "ok", "output_dir": str(args.output_dir), **summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
