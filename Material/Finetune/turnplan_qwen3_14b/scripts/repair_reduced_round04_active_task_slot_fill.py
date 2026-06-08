from __future__ import annotations

import json
from collections import Counter

from reduced_round04_dataset_utils import (
    append_curation_note,
    clone_record,
    dataset_output_dir,
    extract_slot,
    extract_slots,
    focused_title,
    get_target_slot,
    load_canonical_records,
    set_history,
    stable_pick,
    write_jsonl,
)


OUTPUT_DIR = dataset_output_dir("reduced_round04_active_task_slot_fill_repair_v1")

URGE_ASSISTANT = [
    "我接着看这单，您直接说为什么着急就行。",
    "好，我继续跟进。您说一下想催的原因就行。",
    "行，这单我接着处理。您补一句现在最着急的情况就可以。",
]
URGE_LEAD = [
    ("user", "刚才那单接着说"),
    ("assistant", None),
]

COMPLAINT_ASSISTANT = [
    "可以，继续走投诉。您说下主要不满的地方就行。",
    "好，我接着记。您直接说为什么要投诉。",
    "行，这条我继续处理。您补一句具体为什么不满意。",
]
COMPLAINT_LEAD = [
    ("user", "那就接着刚才那个说"),
    ("assistant", None),
]

PHONE_ASSISTANT = [
    "好，接着这个单。留个能联系到您的电话就行。",
    "行，我继续记。您给我一个联系电话。",
    "这边继续处理，麻烦留个手机号。",
]
PHONE_LEAD = [
    ("user", "这个接着办"),
    ("assistant", None),
]

RULE_ASSISTANT = [
    "好，那就继续这个。您说一下想问哪方面的规则。",
    "行，这里还差一个具体主题，您直接说就行。",
    "可以，接着问。您把想了解的那块规则说出来。",
]
RULE_LEAD = [
    ("user", "那就接着这个问"),
    ("assistant", None),
    ("user", "还差哪部分"),
    ("assistant", None),
]

SERVICE_ASSISTANT = [
    "行，这个继续。您直接说是哪一个服务项目。",
    "好，我接着看。您把要问的项目名说出来就行。",
    "可以，继续这条。您具体说是哪个服务项目。",
]
SERVICE_LEAD = [
    ("user", "刚才那个接着看"),
    ("assistant", None),
    ("user", "还要我补什么"),
    ("assistant", None),
]

CONFIRM_ASSISTANT = [
    "好，这边继续。您确认一下这条投诉还提不提交。",
    "行，我接着往下走。您说一声要不要提交就可以。",
    "可以，还是这个。您确认下这条投诉是否继续提交。",
]
CONFIRM_LEAD = [
    ("user", "就继续刚才那条"),
    ("assistant", None),
    ("user", "现在还差什么"),
    ("assistant", None),
]

RULE_MESSAGE_TEMPLATES = {
    "物业服务": ["先看物业服务", "我想问物业服务这块", "物业服务这方面"],
    "物业费": ["物业费怎么收", "我想问物业费", "先说物业费这块"],
    "装修报备": ["装修报备怎么弄", "我想问装修报备", "先看装修报备"],
    "停车规则": ["停车这块怎么规定", "我想问停车规则", "先说停车这块"],
    "宠物管理": ["宠物这块有什么要求", "我想问宠物管理", "先看宠物这块"],
    "社区公约": ["社区公约这块", "我想问社区公约", "先说社区公约"],
}

SERVICE_MESSAGE_TEMPLATES = {
    "净水器滤芯更换": ["净水器滤芯更换这个", "我问净水器滤芯更换", "就是净水器滤芯更换"],
    "燃气报警器换新": ["燃气报警器换新这个", "我想看燃气报警器换新", "就是燃气报警器换新"],
    "地漏疏通": ["地漏疏通这个", "我问地漏疏通", "就是地漏疏通"],
    "窗纱更换": ["窗纱更换这个", "我想看窗纱更换", "就问窗纱更换"],
    "空调清洗": ["空调清洗这个", "我问空调清洗", "就是空调清洗"],
    "入户深度保洁": ["入户深度保洁这个", "我想看入户深度保洁", "就问入户深度保洁"],
    "可视对讲检修": ["可视对讲检修这个", "我问可视对讲检修", "就看可视对讲检修"],
}

CONFIRM_TRUE_MESSAGES = [
    "行，那就提吧",
    "可以，直接提交",
    "确认，继续提",
    "嗯，就按投诉提上去",
]
CONFIRM_FALSE_MESSAGES = [
    "先别提了",
    "算了，这条先放放",
    "先不提交了",
]


def build_history(record: dict, assistant_options: list[str], lead_template: list[tuple[str, str | None]], salt: str) -> None:
    assistant_text = stable_pick(assistant_options, record["id"], salt)
    messages: list[tuple[str, str]] = []
    for role, text in lead_template:
        if text is None:
            messages.append((role, assistant_text))
        else:
            messages.append((role, text))
    set_history(record, messages)


def patch_urge_reason(record: dict) -> None:
    build_history(record, URGE_ASSISTANT, URGE_LEAD, "urge")


def patch_complaint_reason(record: dict) -> None:
    build_history(record, COMPLAINT_ASSISTANT, COMPLAINT_LEAD, "complaint")


def patch_contact_phone(record: dict) -> None:
    build_history(record, PHONE_ASSISTANT, PHONE_LEAD, "phone")


def patch_rule_topic(record: dict) -> None:
    build_history(record, RULE_ASSISTANT, RULE_LEAD, "rule")
    topic = extract_slot(record, "rule_topic") or ""
    candidates = RULE_MESSAGE_TEMPLATES.get(topic, [topic])
    record["input"]["user_message"] = stable_pick(candidates, record["id"], "rule_user")


def patch_service_item(record: dict) -> None:
    build_history(record, SERVICE_ASSISTANT, SERVICE_LEAD, "service")
    title = focused_title(record)
    candidates = SERVICE_MESSAGE_TEMPLATES.get(title, [title])
    record["input"]["user_message"] = stable_pick(candidates, record["id"], "service_user")


def patch_complaint_confirm(record: dict) -> None:
    build_history(record, CONFIRM_ASSISTANT, CONFIRM_LEAD, "confirm")
    command = (record["output"].get("task") or {}).get("commands", [{}])[0]
    if command.get("command") == "cancel_flow":
        record["input"]["user_message"] = stable_pick(CONFIRM_FALSE_MESSAGES, record["id"], "confirm_false")
        return
    record["input"]["user_message"] = stable_pick(CONFIRM_TRUE_MESSAGES, record["id"], "confirm_true")


def repair_record(record: dict) -> dict:
    repaired = clone_record(record)
    target_slot = get_target_slot(repaired)
    if target_slot == "urge_reason":
        patch_urge_reason(repaired)
    elif target_slot == "complaint_reason":
        patch_complaint_reason(repaired)
    elif target_slot == "contact_phone":
        patch_contact_phone(repaired)
    elif target_slot == "rule_topic":
        patch_rule_topic(repaired)
    elif target_slot == "service_item_id":
        patch_service_item(repaired)
    elif target_slot == "complaint_confirm":
        patch_complaint_confirm(repaired)
    append_curation_note(repaired, "round04_active_task_slot_fill_repair_v1")
    return repaired


def build_manifest(rows: list[dict]) -> dict:
    counts = Counter((row["split"], get_target_slot(row) or "unknown") for row in rows)
    return {
        "dataset_id": OUTPUT_DIR.name,
        "source_dataset": "canonical_llm",
        "bucket": "active_task_slot_fill",
        "total_records": len(rows),
        "split_slot_counts": {
            f"{split}:{slot}": count for (split, slot), count in sorted(counts.items())
        },
        "record_ids": [row["id"] for row in rows],
    }


def build_summary(manifest: dict) -> str:
    lines = [
        "# reduced_round04_active_task_slot_fill_repair_v1 Summary",
        "",
        "- source dataset: `canonical_llm`",
        "- purpose: repair active-task slot-fill samples by strengthening task lead-in and slot-target alignment.",
        "",
        f"- total_records: `{manifest['total_records']}`",
        "",
        "| split:slot | count |",
        "| --- | ---: |",
    ]
    for key, count in manifest["split_slot_counts"].items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "## Repair focus",
            "",
            "- strengthen `history -> active_task -> current slot fill` continuity",
            "- keep short continuation utterances, but make the lead-in explicit enough to be learnable",
            "- preserve cancel-vs-confirm contrast inside `complaint_confirm`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    rows = [repair_record(row) for row in load_canonical_records("active_task_slot_fill")]
    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "val"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUTPUT_DIR / "records_train.jsonl", train_rows)
    write_jsonl(OUTPUT_DIR / "records_val.jsonl", val_rows)
    manifest = build_manifest(rows)
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "summary.md").write_text(build_summary(manifest), encoding="utf-8")
    print(json.dumps({"output_dir": str(OUTPUT_DIR), "train": len(train_rows), "val": len(val_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
