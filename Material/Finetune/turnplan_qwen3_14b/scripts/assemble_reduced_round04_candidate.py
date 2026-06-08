from __future__ import annotations

import json
import sys
from collections import Counter

from reduced_round04_contract import DATASET_SCRIPTS_DIR, KEEP_BASE_OUTPUT_DIR
from reduced_round04_dataset_utils import dataset_output_dir, load_jsonl, stable_pick, write_jsonl

sys.path.insert(0, str(DATASET_SCRIPTS_DIR))
from audit_helpers import enrich_records  # noqa: E402
from input_sanitizer import sanitize_record_input  # noqa: E402
from metrics import record_signature  # noqa: E402


ACTIVE_FIX_DIR = dataset_output_dir("reduced_round04_active_task_slot_fill_repair_v1")
AMBIGUOUS_REBUILD_DIR = dataset_output_dir("reduced_round04_ambiguous_all_null_rebuild_v1")
EXIT_REBUILD_DIR = dataset_output_dir("reduced_round04_directive_exit_runtime_rebuild_v1")
OUTPUT_DIR = dataset_output_dir("reduced_round04_candidate_v1")
EXPORT_DIR = dataset_output_dir("reduced_round04_candidate_v1_exports_llm")

ACTIVE_RULE_TOPIC_VARIANTS = {
    "物业服务": ["先看物业服务", "我想问物业服务这块", "物业服务这方面", "先说物业服务", "物业服务这块我想了解下"],
    "物业费": ["物业费怎么收", "我想问物业费", "先说物业费这块", "物业费这边我想了解下"],
    "装修报备": ["装修报备怎么弄", "我想问装修报备", "先看装修报备", "装修报备这块我想了解下"],
    "停车规则": ["停车这块怎么规定", "我想问停车规则", "先说停车这块", "停车规则我想了解下"],
    "宠物管理": ["宠物这块有什么要求", "我想问宠物管理", "先看宠物这块", "宠物管理这边我想问下"],
    "社区公约": ["社区公约这块", "我想问社区公约", "先说社区公约", "社区公约这边我想了解下"],
}
ACTIVE_SERVICE_ITEM_VARIANTS = {
    "净水器滤芯更换": ["净水器滤芯更换这个", "我问净水器滤芯更换", "就是净水器滤芯更换", "净水器滤芯更换这项"],
    "燃气报警器换新": ["燃气报警器换新这个", "我想看燃气报警器换新", "就是燃气报警器换新", "燃气报警器换新这项"],
    "地漏疏通": ["地漏疏通这个", "我问地漏疏通", "就是地漏疏通", "地漏疏通这项"],
    "窗纱更换": ["窗纱更换这个", "我想看窗纱更换", "就问窗纱更换", "窗纱更换这项"],
    "空调清洗": ["空调清洗这个", "我问空调清洗", "就是空调清洗", "空调清洗这项"],
    "入户深度保洁": ["就问入户深度保洁", "入户深度保洁这个", "我想看入户深度保洁", "入户深度保洁这项"],
    "可视对讲检修": ["可视对讲检修这个", "我问可视对讲检修", "就看可视对讲检修", "可视对讲检修这项"],
}
AMBIGUOUS_VARIANTS = {
    "门牌上那个名字能改吗": ["门牌上那个名字能改吗", "门牌那个名字能改吗", "门牌上的名字能改一下吗"],
    "门牌名字想改一下": ["门牌名字想改一下", "我想把门牌名字改一下", "门牌名字这边想调一下"],
    "发票这事怎么办": ["发票这事怎么办", "发票这个该怎么弄", "开发票这事怎么办"],
    "小区发票怎么开": ["小区发票怎么开", "小区的发票怎么开", "发票如果开小区抬头该怎么弄"],
    "我想开个小区发票": ["我想开个小区发票", "我这边想开个小区发票", "想开张小区发票"],
    "隔壁装修现在什么情况": ["隔壁装修现在什么情况", "隔壁那家装修现在什么情况", "旁边那户装修现在怎么样"],
    "门锁密码这边怎么搞": ["门锁密码这边怎么搞", "门锁密码这事怎么弄", "门锁密码这边要怎么处理"],
    "我想把门锁密码处理一下": ["我想把门锁密码处理一下", "我想把门锁密码弄一下", "门锁密码我想处理一下"],
    "那个门锁密码能帮我看看吗": ["那个门锁密码能帮我看看吗", "门锁密码这事能帮我看看吗", "门锁密码这边能帮我看看吗"],
}
EXIT_VARIANTS = {
    "先不催这个了，我想说别的": ["先不催这个了，我想说别的", "这个先别催了，我另外问个事", "催办这事先停一下，我想说别的"],
    "先别查这个了，回头再说": ["先别查这个了，回头再说", "这个先别查了，晚点再说", "先不看这个了，回头再聊"],
    "这个催办先停一下": ["这个催办先停一下", "这条催办先放一放", "这个先别往下催了"],
    "这个先放一放，我想聊别的": ["这个先放一放，我想聊别的", "这事先放着吧，我想说别的", "这个先搁一下，我聊点别的"],
    "先别往下催了，我换个话题": ["先别往下催了，我换个话题", "催办这边先停一下，我换个话题", "这个先别催了，我换个话题"],
    "先到这吧，我另外问个事": ["先到这吧，我另外问个事", "这个先说到这儿，我另外问个事", "先聊到这儿吧，我再问个别的"],
    "这个先看到这吧，我问点别的": ["这个先看到这吧，我问点别的", "先看到这儿吧，我想问别的", "这个先放这儿，我再问个别的"],
    "先不说这个了，我们换个话题吧": ["先不说这个了，我们换个话题吧", "这个先不聊了，我们换个话题", "先别说这个了，咱们聊别的"],
    "这条投诉先别往下提了": ["这条投诉先别往下提了", "这条投诉先停一下", "这个投诉先别继续往下走了"],
    "先停这儿吧，我想换个话题": ["先停这儿吧，我想换个话题", "先到这儿吧，我想换个话题", "这事先停一下，我换个话题"],
}


def load_records(dataset_dir) -> list[dict]:
    rows = load_jsonl(dataset_dir / "records_train.jsonl")
    rows.extend(load_jsonl(dataset_dir / "records_val.jsonl"))
    return rows


def _apply_first_unused(candidates: list[str], current: str, used: set[str]) -> str | None:
    for candidate in candidates:
        if candidate != current and candidate not in used:
            return candidate
    for candidate in candidates:
        if candidate != current:
            return candidate
    return None


def dedupe_exact_pairs(rows: list[dict]) -> int:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(record_signature(row), []).append(row)

    changed = 0
    used_by_bucket: dict[str, set[str]] = {}
    for row in rows:
        used_by_bucket.setdefault(row["bucket"], set()).add(row["input"]["user_message"])

    for items in groups.values():
        if len(items) <= 1:
            continue
        anchor = items[0]
        for index, row in enumerate(items[1:], start=1):
            bucket = row["bucket"]
            current = row["input"]["user_message"]
            used = used_by_bucket[bucket]
            replacement = build_replacement_message(row, anchor, index, used)
            if replacement and replacement != current:
                row["input"]["user_message"] = replacement
                used.add(replacement)
                changed += 1
    return changed


def build_replacement_message(row: dict, anchor: dict, index: int, used: set[str]) -> str | None:
    bucket = row["bucket"]
    current = row["input"]["user_message"]
    if bucket == "active_task_slot_fill":
        active_system_task = row["input"].get("active_system_task") or {}
        slot_name = active_system_task.get("slot_name")
        if slot_name == "rule_topic":
            topic = ((row["output"].get("task") or {}).get("commands") or [{}])[0].get("slots", {}).get("rule_topic")
            candidates = ACTIVE_RULE_TOPIC_VARIANTS.get(topic, [current])
            return _apply_first_unused(candidates, current, used)
        if slot_name == "service_item_id":
            title = ((row["input"].get("focused_object") or {}).get("title")) or current
            candidates = ACTIVE_SERVICE_ITEM_VARIANTS.get(title, [current])
            return _apply_first_unused(candidates, current, used)
        return f"{current}。"
    if bucket == "ambiguous_all_null":
        candidates = AMBIGUOUS_VARIANTS.get(current)
        if candidates:
            return _apply_first_unused(candidates, current, used)
        return f"{current}？" if not current.endswith(("吗", "？", "?")) else f"{current}吧"
    if bucket == "directive_exit_runtime":
        candidates = EXIT_VARIANTS.get(current)
        if candidates:
            return _apply_first_unused(candidates, current, used)
        return f"{current}吧"
    return None


def validate_reduced_rows(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    ids = set()
    for row in rows:
        if row["id"] in ids:
            errors.append(f"duplicate id: {row['id']}")
        ids.add(row["id"])
        if row["bucket"] == "active_task_slot_fill":
            if row["input"].get("active_task") is None:
                errors.append(f"{row['id']}: missing active_task")
            if row["input"].get("active_system_task") is None:
                errors.append(f"{row['id']}: missing active_system_task")
        if row["bucket"] == "ambiguous_all_null":
            if any(row["output"].get(track) is not None for track in ("task", "knowledge", "chitchat", "directive")):
                errors.append(f"{row['id']}: ambiguous_all_null not all-null")
        if row["bucket"] == "directive_exit_runtime":
            if row["output"].get("directive") != {"action": "exit_runtime"}:
                errors.append(f"{row['id']}: exit_runtime output mismatch")
        sanitized = sanitize_record_input(row["input"])
        if set(sanitized.keys()) != {
            "history",
            "runtime_state",
            "active_task",
            "active_system_task",
            "paused_tasks",
            "focused_object",
            "user_message",
        }:
            errors.append(f"{row['id']}: sanitized input keys mismatch")
    return errors


def build_manifest(rows: list[dict]) -> dict:
    bucket_counts = Counter((row["bucket"], row["split"]) for row in rows)
    enriched = enrich_records(rows)
    safe_rows = [row for row in enriched if row["audit_meta"]["passed_for_sft"]]
    return {
        "dataset_id": OUTPUT_DIR.name,
        "source_datasets": [
            KEEP_BASE_OUTPUT_DIR.name,
            ACTIVE_FIX_DIR.name,
            AMBIGUOUS_REBUILD_DIR.name,
            EXIT_REBUILD_DIR.name,
        ],
        "total_records": len(rows),
        "bucket_counts": {
            bucket: {
                "train": bucket_counts.get((bucket, "train"), 0),
                "val": bucket_counts.get((bucket, "val"), 0),
            }
            for bucket in sorted({row["bucket"] for row in rows})
        },
        "sft_ready_records": len(safe_rows),
        "unsafe_records": [row["id"] for row in enriched if not row["audit_meta"]["passed_for_sft"]],
    }


def build_summary(manifest: dict) -> str:
    lines = [
        "# reduced_round04_candidate_v1 Summary",
        "",
        f"- source datasets: `{', '.join(manifest['source_datasets'])}`",
        "- purpose: assemble the reduced round_04 candidate after keep/fix/rebuild passes.",
        "",
        f"- total_records: `{manifest['total_records']}`",
        f"- sft_ready_records: `{manifest['sft_ready_records']}`",
        f"- unsafe_records: `{len(manifest['unsafe_records'])}`",
        "",
        "| bucket | train | val |",
        "| --- | ---: | ---: |",
    ]
    for bucket, counts in manifest["bucket_counts"].items():
        lines.append(f"| `{bucket}` | {counts['train']} | {counts['val']} |")
    if manifest["unsafe_records"]:
        lines.extend(["", "## Unsafe IDs", ""])
        for record_id in manifest["unsafe_records"]:
            lines.append(f"- `{record_id}`")
    return "\n".join(lines)


def to_sft_record(record: dict, system_prompt: str) -> dict:
    return {
        "id": record["id"],
        "bucket": record["bucket"],
        "source": record["source"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(sanitize_record_input(record["input"]), ensure_ascii=False, indent=2)},
            {"role": "assistant", "content": json.dumps(record["output"], ensure_ascii=False, indent=2)},
        ],
        "meta": {
            **record["meta"],
            "semantic_meta": record.get("semantic_meta"),
            "audit_meta": record.get("audit_meta"),
        },
    }


def export_sft(rows: list[dict]) -> None:
    from dataset_contract import SYSTEM_PROMPT  # type: ignore  # noqa: E402

    enriched = enrich_records(rows)
    safe_rows = [row for row in enriched if row["audit_meta"]["passed_for_sft"]]
    train_rows = [row for row in safe_rows if row["split"] == "train"]
    val_rows = [row for row in safe_rows if row["split"] == "val"]
    write_jsonl(EXPORT_DIR / "sft_train.jsonl", [to_sft_record(row, SYSTEM_PROMPT) for row in train_rows])
    write_jsonl(EXPORT_DIR / "sft_val.jsonl", [to_sft_record(row, SYSTEM_PROMPT) for row in val_rows])


def main() -> None:
    rows = []
    rows.extend(load_records(KEEP_BASE_OUTPUT_DIR))
    rows.extend(load_records(ACTIVE_FIX_DIR))
    rows.extend(load_records(AMBIGUOUS_REBUILD_DIR))
    rows.extend(load_records(EXIT_REBUILD_DIR))
    dedupe_exact_pairs(rows)
    errors = validate_reduced_rows(rows)
    if errors:
        raise SystemExit(json.dumps(errors[:50], ensure_ascii=False, indent=2))
    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "val"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUTPUT_DIR / "records_train.jsonl", train_rows)
    write_jsonl(OUTPUT_DIR / "records_val.jsonl", val_rows)
    manifest = build_manifest(rows)
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "summary.md").write_text(build_summary(manifest), encoding="utf-8")
    export_sft(rows)
    print(
        json.dumps(
            {
                "output_dir": str(OUTPUT_DIR),
                "export_dir": str(EXPORT_DIR),
                "train": len(train_rows),
                "val": len(val_rows),
                "sft_ready_records": manifest["sft_ready_records"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
