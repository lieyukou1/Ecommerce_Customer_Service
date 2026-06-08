from __future__ import annotations

import json
from collections import Counter

from reduced_round04_dataset_utils import (
    append_curation_note,
    clone_record,
    dataset_output_dir,
    focused_title,
    get_target_slot,
    load_canonical_records,
    set_history,
    stable_pick,
    write_jsonl,
)


OUTPUT_DIR = dataset_output_dir("reduced_round04_directive_exit_runtime_rebuild_v1")

KNOWLEDGE_USER_MESSAGES = [
    "先不说这个了，我们换个话题吧",
    "这个先放一放，我想聊别的",
    "先到这吧，我另外问个事",
    "这个先不看了，回头再说",
]

ACTIVE_TASK_EXIT_MESSAGES = {
    "work_order_urge_submission": [
        "先不催这个了，我想说别的",
        "这单先放一下，回头再催",
        "先别往下催了，我换个话题",
        "这个催办先停一下",
    ],
    "complaint_request_submission": [
        "这条投诉先别往下提了",
        "先停这儿吧，我想换个话题",
        "这个先不继续投诉了",
        "这事先放一放，我说别的",
    ],
    "work_order_status_query": [
        "先不看这个进度了",
        "这个先看到这吧，我问点别的",
        "先别查这个了，回头再说",
        "这个先放着，我换个话题",
    ],
}

KNOWLEDGE_HISTORY = [
    ("user", "刚才那个我先了解一下"),
    ("assistant", None),
]

ACTIVE_TASK_HISTORY = {
    "work_order_urge_submission": [
        ("user", "那就接着这单说"),
        ("assistant", "行，这条我继续跟进。"),
        ("assistant", None),
    ],
    "complaint_request_submission": [
        ("user", "还是刚才那条继续"),
        ("assistant", "好，这边继续按投诉往下走。"),
        ("assistant", None),
    ],
    "work_order_status_query": [
        ("user", "就看刚才那条的情况"),
        ("assistant", "行，我继续看这单现在的进展。"),
        ("assistant", None),
    ],
}

ACTIVE_TASK_ASSISTANT_BY_SLOT = {
    "urge_reason": [
        "您直接说下为什么着急，我这边记一下。",
        "您补一句现在最着急的情况就行。",
        "您说下想催的原因，我继续往下记。",
    ],
    "complaint_reason": [
        "您直接说下具体为什么不满意。",
        "您补一句主要想投诉的原因就行。",
        "您说下最不满的地方，我记一下。",
    ],
    "complaint_confirm": [
        "您确认一下，这条投诉要不要继续提交。",
        "您说一声这条投诉还提不提交就行。",
        "现在就差您确认，这条投诉是否继续往下提。",
    ],
}

KNOWLEDGE_ASSISTANT_BY_OBJECT = {
    "service_item": [
        "可以，我先给您说说这个服务项目。",
        "行，我先按这个项目给您介绍一下。",
        "好，我先围绕这个项目跟您说一下。",
    ],
    "work_order": [
        "可以，我先跟您说说这单现在的情况。",
        "行，我先围绕这单给您看一下。",
        "好，我先就这个给您说一下。",
    ],
}


def build_knowledge_history(record: dict) -> None:
    focused_object = record["input"].get("focused_object") or {}
    object_type = focused_object.get("type") or "work_order"
    assistant = stable_pick(KNOWLEDGE_ASSISTANT_BY_OBJECT[object_type], record["id"], "knowledge_assistant")
    messages: list[tuple[str, str]] = []
    for role, text in KNOWLEDGE_HISTORY:
        messages.append((role, assistant if text is None else text))
    set_history(record, messages)


def build_active_task_history(record: dict) -> None:
    active_task = record["input"].get("active_task") or {}
    flow_id = active_task.get("flow_id") or "work_order_urge_submission"
    target_slot = get_target_slot(record)
    assistant_choices = ACTIVE_TASK_ASSISTANT_BY_SLOT.get(target_slot or "", [])
    if not assistant_choices:
        assistant_choices = ["我这边接着看，您直接说就行。"]
    prompt = stable_pick(assistant_choices, record["id"], "active_prompt")
    messages = []
    for role, text in ACTIVE_TASK_HISTORY[flow_id]:
        messages.append((role, prompt if text is None else text))
    set_history(record, messages)


def rebuild_record(record: dict) -> dict:
    rebuilt = clone_record(record)
    state = rebuilt["input"]["runtime_state"]["conversation_state"]
    if state == "FOCUSED_KNOWLEDGE":
        build_knowledge_history(rebuilt)
        rebuilt["input"]["user_message"] = stable_pick(KNOWLEDGE_USER_MESSAGES, rebuilt["id"], "knowledge_user")
        rebuilt["input"]["active_task"] = None
        rebuilt["input"]["active_system_task"] = None
        rebuilt["input"]["paused_tasks"] = []
    else:
        build_active_task_history(rebuilt)
        flow_id = (rebuilt["input"].get("active_task") or {}).get("flow_id") or "work_order_urge_submission"
        rebuilt["input"]["user_message"] = stable_pick(
            ACTIVE_TASK_EXIT_MESSAGES[flow_id],
            rebuilt["id"],
            "active_user",
        )
        rebuilt["input"]["paused_tasks"] = []
    append_curation_note(rebuilt, "round04_directive_exit_runtime_rebuild_v1")
    return rebuilt


def build_manifest(rows: list[dict]) -> dict:
    split_counts = Counter(row["split"] for row in rows)
    state_counts = Counter(row["input"]["runtime_state"]["conversation_state"] for row in rows)
    flow_counts = Counter(
        ((row["input"].get("active_task") or {}).get("flow_id") or "focused_knowledge")
        for row in rows
    )
    return {
        "dataset_id": OUTPUT_DIR.name,
        "source_dataset": "canonical_llm",
        "bucket": "directive_exit_runtime",
        "total_records": len(rows),
        "split_counts": dict(split_counts),
        "state_counts": dict(state_counts),
        "flow_counts": dict(flow_counts),
        "record_ids": [row["id"] for row in rows],
    }


def build_summary(manifest: dict) -> str:
    lines = [
        "# reduced_round04_directive_exit_runtime_rebuild_v1 Summary",
        "",
        "- source dataset: `canonical_llm`",
        "- purpose: rebuild exit-runtime samples so every exit has believable runtime lead-in.",
        "",
        f"- total_records: `{manifest['total_records']}`",
        f"- split_counts: `{manifest['split_counts']}`",
        "",
        "## State counts",
        "",
    ]
    for state, count in sorted(manifest["state_counts"].items()):
        lines.append(f"- `{state}`: `{count}`")
    lines.extend(
        [
            "",
            "## Flow counts",
            "",
        ]
    )
    for flow_id, count in sorted(manifest["flow_counts"].items()):
        lines.append(f"- `{flow_id}`: `{count}`")
    lines.extend(
        [
            "",
            "## Rebuild focus",
            "",
            "- add concrete lead-in before every `exit_runtime`",
            "- keep exit language short and natural",
            "- separate knowledge-context exits from active-task exits",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    rows = [rebuild_record(row) for row in load_canonical_records("directive_exit_runtime")]
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
