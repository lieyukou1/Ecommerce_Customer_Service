from __future__ import annotations

import json
from collections import Counter, defaultdict

from reduced_round04_dataset_utils import (
    append_curation_note,
    clone_record,
    dataset_output_dir,
    focused_title,
    load_canonical_records,
    set_history,
    stable_pick,
    write_jsonl,
)


OUTPUT_DIR = dataset_output_dir("reduced_round04_ambiguous_all_null_rebuild_v1")

SCENARIO_MESSAGES = {
    "doorplate_name": [
        "门牌名字想改一下",
        "门牌上那个名字能改吗",
        "我想把门牌显示的名字换一下",
        "门口那个名字不对，想改改",
        "门牌显示能不能调整一下",
    ],
    "community_invoice": [
        "小区发票怎么开",
        "我想开个小区发票",
        "发票这事怎么办",
        "能开小区发票吗",
        "我这边想弄张发票",
    ],
    "neighbor_renovation": [
        "邻居装修到哪一步了",
        "隔壁装修现在什么情况",
        "旁边那户装修进度能查吗",
        "邻居家装修现在做到哪了",
        "隔壁那家装修有没有新进展",
    ],
    "door_lock_password": [
        "门锁密码这事能弄吗",
        "我想把门锁密码处理一下",
        "门锁密码这边怎么搞",
        "那个门锁密码能帮我看看吗",
        "远程重置门锁密码可以吗",
    ],
}

STATE_ORDER = ["IDLE", "CLARIFYING", "FOCUSED_KNOWLEDGE", "ACTIVE_TASK", "TRANSITIONING"]

HISTORY_BY_STATE = {
    "IDLE": [],
    "CLARIFYING": [
        ("user", "我有个事想问"),
        ("assistant", "您说，我先听一下具体是什么。"),
    ],
    "FOCUSED_KNOWLEDGE": [
        ("user", "刚才那个先放着，我另外问个事"),
        ("assistant", "可以，您直接说。"),
    ],
    "ACTIVE_TASK": [
        ("user", "先接着刚才那单说"),
        ("assistant", "行，这条我继续看着。"),
        ("user", "不过我突然想到另一个事"),
        ("assistant", "您说，我先听一下是什么。"),
    ],
    "TRANSITIONING": [
        ("user", "刚才那个先别往下走"),
        ("assistant", "好，那我先停在这里。"),
        ("user", "我还有个别的事想问"),
        ("assistant", "可以，您说。"),
    ],
}


def scenario_key(record: dict) -> str:
    text = record["input"]["user_message"]
    if "门牌" in text:
        return "doorplate_name"
    if "发票" in text:
        return "community_invoice"
    if "邻居" in text or "隔壁" in text:
        return "neighbor_renovation"
    return "door_lock_password"


def rebuild_record(record: dict) -> dict:
    rebuilt = clone_record(record)
    state = rebuilt["input"]["runtime_state"]["conversation_state"]
    scenario = scenario_key(rebuilt)
    rebuilt["input"]["user_message"] = stable_pick(SCENARIO_MESSAGES[scenario], rebuilt["id"], state)
    set_history(rebuilt, HISTORY_BY_STATE[state])

    if state in {"IDLE", "CLARIFYING"}:
        rebuilt["input"]["focused_object"] = None
        rebuilt["input"]["active_task"] = None
        rebuilt["input"]["active_system_task"] = None
        rebuilt["input"]["paused_tasks"] = []
    elif state == "FOCUSED_KNOWLEDGE":
        rebuilt["input"]["active_task"] = None
        rebuilt["input"]["active_system_task"] = None
        rebuilt["input"]["paused_tasks"] = []
    elif state == "ACTIVE_TASK":
        rebuilt["input"]["active_system_task"] = None
        rebuilt["input"]["paused_tasks"] = []
    elif state == "TRANSITIONING":
        rebuilt["input"]["active_task"] = None
        rebuilt["input"]["active_system_task"] = None

    append_curation_note(rebuilt, "round04_ambiguous_all_null_rebuild_v1")
    return rebuilt


def build_manifest(rows: list[dict]) -> dict:
    state_counts = Counter(row["input"]["runtime_state"]["conversation_state"] for row in rows)
    scenario_counts = Counter(scenario_key(row) for row in rows)
    split_counts = Counter(row["split"] for row in rows)
    return {
        "dataset_id": OUTPUT_DIR.name,
        "source_dataset": "canonical_llm",
        "bucket": "ambiguous_all_null",
        "total_records": len(rows),
        "split_counts": dict(split_counts),
        "state_counts": dict(state_counts),
        "scenario_counts": dict(scenario_counts),
        "record_ids": [row["id"] for row in rows],
    }


def build_summary(manifest: dict) -> str:
    lines = [
        "# reduced_round04_ambiguous_all_null_rebuild_v1 Summary",
        "",
        "- source dataset: `canonical_llm`",
        "- purpose: rebuild ambiguous clarify-trigger samples with natural wording and timeline-consistent context.",
        "",
        f"- total_records: `{manifest['total_records']}`",
        f"- split_counts: `{manifest['split_counts']}`",
        "",
        "| state | count |",
        "| --- | ---: |",
    ]
    for state in STATE_ORDER:
        lines.append(f"| `{state}` | {manifest['state_counts'].get(state, 0)} |")
    lines.extend(
        [
            "",
            "## Scenario coverage",
            "",
        ]
    )
    for scenario, count in sorted(manifest["scenario_counts"].items()):
        lines.append(f"- `{scenario}`: `{count}`")
    lines.extend(
        [
            "",
            "## Rebuild focus",
            "",
            "- remove template residue and fake helper phrasing",
            "- keep ambiguity genuine: user asks for something, but the flow is still underdetermined",
            "- restore state-specific lead-in so `all_null / clarify fallback` is tied to believable context",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    rows = [rebuild_record(row) for row in load_canonical_records("ambiguous_all_null")]
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
