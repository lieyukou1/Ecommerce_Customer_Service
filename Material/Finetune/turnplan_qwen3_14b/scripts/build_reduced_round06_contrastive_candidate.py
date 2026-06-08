from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

from reduced_round04_contract import CANONICAL_LLM_DIR, DATASET_SCRIPTS_DIR
from reduced_round04_dataset_utils import append_curation_note, load_jsonl, write_jsonl


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1"
BASESET_DIR = DATASET_ROOT / "reduced_round04_candidate_v1"
OUTPUT_DIR = DATASET_ROOT / "reduced_round06_contrastive_candidate_v1"

sys.path.insert(0, str(DATASET_SCRIPTS_DIR))
from audit_helpers import enrich_records  # noqa: E402
from input_sanitizer import sanitize_record_input  # noqa: E402


def load_rows(dataset_dir: Path) -> list[dict]:
    rows = load_jsonl(dataset_dir / "records_train.jsonl")
    rows.extend(load_jsonl(dataset_dir / "records_val.jsonl"))
    return rows


def build_task_output(command_name: str, slots: dict[str, str] | None = None, flow: str | None = None) -> dict:
    command: dict[str, object] = {"command": command_name}
    if flow is not None:
        command["flow"] = flow
    if slots is not None:
        command["slots"] = slots
    return {
        "task": {"commands": [command]},
        "knowledge": None,
        "chitchat": None,
        "directive": None,
    }


def build_knowledge_output(intent: str) -> dict:
    return {
        "task": None,
        "knowledge": {"intents": [intent]},
        "chitchat": None,
        "directive": None,
    }


def build_all_null_output() -> dict:
    return {
        "task": None,
        "knowledge": None,
        "chitchat": None,
        "directive": None,
    }


def build_exit_output() -> dict:
    return {
        "task": None,
        "knowledge": None,
        "chitchat": None,
        "directive": {"action": "exit_runtime"},
    }


def base_clone(anchor: dict, *, new_id: str, bucket: str, user_message: str, output: dict) -> dict:
    row = deepcopy(anchor)
    row["id"] = new_id
    row["source"] = "contrastive-augmentation"
    row["bucket"] = bucket
    row["split"] = "train"
    row["input"]["user_message"] = user_message
    row["output"] = output
    return row


def set_standalone_context(
    row: dict,
    *,
    conversation_state: str,
    last_route_semantic_kind: str | None,
    focused_object: dict | None,
    history: list[tuple[str, str]],
) -> None:
    row["input"]["history"] = [{"role": role, "text": text} for role, text in history]
    row["input"]["runtime_state"] = {
        "conversation_state": conversation_state,
        "last_route": (
            None if last_route_semantic_kind is None else {"track": "knowledge", "semantic_kind": last_route_semantic_kind}
        ),
        "last_task_outcome": None,
    }
    row["input"]["active_task"] = None
    row["input"]["active_system_task"] = None
    row["input"]["paused_tasks"] = []
    row["input"]["focused_object"] = deepcopy(focused_object)


def finalize_row(
    row: dict,
    *,
    contrast_group: str,
    note: str,
    notes_suffix: str,
) -> dict:
    meta = dict(row.get("meta", {}))
    meta["notes"] = note
    meta["contrast_group"] = contrast_group
    row["meta"] = meta
    append_curation_note(row, notes_suffix)
    enriched = enrich_records([row])[0]
    semantic_meta = dict(enriched.get("semantic_meta") or {})
    semantic_meta["contrast_group"] = contrast_group
    enriched["semantic_meta"] = semantic_meta
    audit_meta = enriched.get("audit_meta") or {}
    if audit_meta.get("passed_for_sft") is not True:
        raise ValueError(f"{row['id']} failed audit: {audit_meta.get('audit_notes')}")
    sanitize_record_input(enriched["input"])
    return enriched


def make_community_rule_pairs(base_rows: dict[str, dict], canonical_rows: dict[str, dict]) -> list[dict]:
    task_anchor = base_rows["tp_active_task_slot_fill_train_040"]
    knowledge_anchors = [
        canonical_rows["tp_service_item_knowledge_train_005"],
        canonical_rows["tp_service_item_knowledge_train_012"],
        canonical_rows["tp_service_item_knowledge_train_019"],
    ]
    phrases = [
        "先说社区公约",
        "社区公约这个",
        "我问社区公约",
    ]
    rows: list[dict] = []
    for index, phrase in enumerate(phrases, start=1):
        group = f"contrast_community_rule_{index:02d}"
        task_row = base_clone(
            task_anchor,
            new_id=f"tp_contrast_community_rule_task_train_{index:03d}",
            bucket="active_task_slot_fill",
            user_message=phrase,
            output=build_task_output("set_slots", {"rule_topic": "社区公约"}),
        )
        rows.append(
            finalize_row(
                task_row,
                contrast_group=group,
                note="active task continuation should treat this phrase as rule_topic slot fill",
                notes_suffix="round06_contrastive_state_pairs_v1",
            )
        )

        knowledge_row = base_clone(
            knowledge_anchors[index - 1],
            new_id=f"tp_contrast_community_rule_knowledge_train_{index:03d}",
            bucket="service_item_knowledge",
            user_message=phrase,
            output=build_knowledge_output("community_rule"),
        )
        rows.append(
            finalize_row(
                knowledge_row,
                contrast_group=group,
                note="without active task, the same phrase should route to community_rule knowledge",
                notes_suffix="round06_contrastive_state_pairs_v1",
            )
        )
    return rows


def make_service_item_pairs(base_rows: dict[str, dict], canonical_rows: dict[str, dict]) -> list[dict]:
    task_anchor = base_rows["tp_active_task_slot_fill_val_007"]
    knowledge_anchor = canonical_rows["tp_service_item_knowledge_train_007"]
    phrases = [
        "我问可视对讲检修",
        "就看可视对讲检修",
        "可视对讲检修这项",
    ]
    rows: list[dict] = []
    for index, phrase in enumerate(phrases, start=1):
        group = f"contrast_service_item_{index:02d}"
        task_row = base_clone(
            task_anchor,
            new_id=f"tp_contrast_service_item_task_train_{index:03d}",
            bucket="active_task_slot_fill",
            user_message=phrase,
            output=build_task_output("set_slots", {"service_item_id": "SVC2008"}),
        )
        task_row["split"] = "train"
        rows.append(
            finalize_row(
                task_row,
                contrast_group=group,
                note="active service-item detail flow should consume this phrase as service_item_id slot fill",
                notes_suffix="round06_contrastive_state_pairs_v1",
            )
        )

        knowledge_row = base_clone(
            knowledge_anchor,
            new_id=f"tp_contrast_service_item_knowledge_train_{index:03d}",
            bucket="service_item_knowledge",
            user_message=phrase,
            output=build_knowledge_output("service_item_info"),
        )
        rows.append(
            finalize_row(
                knowledge_row,
                contrast_group=group,
                note="without active task, the same phrase should stay on service_item_info knowledge",
                notes_suffix="round06_contrastive_state_pairs_v1",
            )
        )
    return rows


def make_cancel_vs_exit_pairs(base_rows: dict[str, dict]) -> list[dict]:
    task_anchors = [
        base_rows["tp_task_interrupt_resume_cancel_train_001"],
        base_rows["tp_task_interrupt_resume_cancel_train_013"],
        base_rows["tp_task_interrupt_resume_cancel_train_021"],
        base_rows["tp_task_interrupt_resume_cancel_train_037"],
    ]
    exit_anchor = base_rows["tp_directive_exit_runtime_train_001"]
    phrases = [
        "这个投诉先不弄了",
        "这个投诉先放一放，不弄了",
        "投诉先撤了吧，不弄了",
        "这单先停一下吧，投诉先不提了",
    ]
    rows: list[dict] = []
    for index, (task_anchor, phrase) in enumerate(zip(task_anchors, phrases, strict=True), start=1):
        group = f"contrast_cancel_exit_{index:02d}"
        task_row = base_clone(
            task_anchor,
            new_id=f"tp_contrast_cancel_task_train_{index:03d}",
            bucket="task_interrupt_resume_cancel",
            user_message=phrase,
            output=build_task_output("cancel_flow"),
        )
        rows.append(
            finalize_row(
                task_row,
                contrast_group=group,
                note="with an active complaint flow, this phrase should cancel the current flow",
                notes_suffix="round06_contrastive_state_pairs_v1",
            )
        )

        exit_row = base_clone(
            exit_anchor,
            new_id=f"tp_contrast_exit_runtime_train_{index:03d}",
            bucket="directive_exit_runtime",
            user_message=phrase,
            output=build_exit_output(),
        )
        rows.append(
            finalize_row(
                exit_row,
                contrast_group=group,
                note="without an active complaint flow, the same phrase should exit the current runtime topic",
                notes_suffix="round06_contrastive_state_pairs_v1",
            )
        )
    return rows


def make_complaint_object_pairs(base_rows: dict[str, dict]) -> list[dict]:
    task_anchors = [
        base_rows["tp_work_order_business_complaint_train_008"],
        base_rows["tp_work_order_business_complaint_train_020"],
    ]
    rows: list[dict] = []
    for index, task_anchor in enumerate(task_anchors, start=1):
        phrase = task_anchor["input"]["user_message"]
        group = f"contrast_complaint_object_{index:02d}"
        task_row = base_clone(
            task_anchor,
            new_id=f"tp_contrast_complaint_task_train_{index:03d}",
            bucket="work_order_business_complaint",
            user_message=phrase,
            output=deepcopy(task_anchor["output"]),
        )
        rows.append(
            finalize_row(
                task_row,
                contrast_group=group,
                note="with a focused work order, this complaint phrase should start complaint submission",
                notes_suffix="round06_contrastive_state_pairs_v1",
            )
        )

        all_null_row = base_clone(
            task_anchor,
            new_id=f"tp_contrast_complaint_all_null_train_{index:03d}",
            bucket="ambiguous_all_null",
            user_message=phrase,
            output=build_all_null_output(),
        )
        set_standalone_context(
            all_null_row,
            conversation_state="IDLE",
            last_route_semantic_kind=None,
            focused_object=None,
            history=[],
        )
        rows.append(
            finalize_row(
                all_null_row,
                contrast_group=group,
                note="without object/runtime context, the same deictic complaint phrase should not auto-open a complaint flow",
                notes_suffix="round06_contrastive_state_pairs_v1",
            )
        )
    return rows


def build_summary(rows: list[dict], added_rows: list[dict]) -> str:
    bucket_counts = Counter((row["bucket"], row["split"]) for row in rows)
    group_counts = Counter(row["semantic_meta"]["contrast_group"] for row in added_rows)
    lines = [
        "# reduced_round06_contrastive_candidate_v1 Summary",
        "",
        "- source dataset: `reduced_round04_candidate_v1`",
        "- purpose: add state-conditioned contrast groups before the next reduced Planner SFT run.",
        "",
        f"- total_records: `{len(rows)}`",
        f"- added_contrastive_train_records: `{len(added_rows)}`",
        "",
        "| bucket | train | val |",
        "| --- | ---: | ---: |",
    ]
    for bucket in sorted({row["bucket"] for row in rows}):
        lines.append(
            f"| `{bucket}` | {bucket_counts.get((bucket, 'train'), 0)} | {bucket_counts.get((bucket, 'val'), 0)} |"
        )
    lines.extend(["", "## Contrast Groups", ""])
    for group_name, count in sorted(group_counts.items()):
        lines.append(f"- `{group_name}`: `{count}` rows")
    return "\n".join(lines) + "\n"


def build_manifest(rows: list[dict], added_rows: list[dict]) -> dict:
    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "val"]
    bucket_counts = defaultdict(lambda: {"train": 0, "val": 0})
    for row in rows:
        bucket_counts[row["bucket"]][row["split"]] += 1
    contrast_groups = defaultdict(list)
    for row in added_rows:
        contrast_groups[row["semantic_meta"]["contrast_group"]].append(row["id"])
    return {
        "dataset_id": OUTPUT_DIR.name,
        "source_dataset": BASESET_DIR.name,
        "train_total": len(train_rows),
        "val_total": len(val_rows),
        "added_contrastive_train_records": len(added_rows),
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "contrast_groups": dict(sorted(contrast_groups.items())),
    }


def main() -> None:
    base_rows = {row["id"]: row for row in load_rows(BASESET_DIR)}
    canonical_rows = {row["id"]: row for row in load_rows(CANONICAL_LLM_DIR)}
    rows = list(base_rows.values())

    added_rows: list[dict] = []
    added_rows.extend(make_community_rule_pairs(base_rows, canonical_rows))
    added_rows.extend(make_service_item_pairs(base_rows, canonical_rows))
    added_rows.extend(make_cancel_vs_exit_pairs(base_rows))
    added_rows.extend(make_complaint_object_pairs(base_rows))

    all_rows = rows + added_rows
    train_rows = [row for row in all_rows if row["split"] == "train"]
    val_rows = [row for row in all_rows if row["split"] == "val"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUTPUT_DIR / "records_train.jsonl", train_rows)
    write_jsonl(OUTPUT_DIR / "records_val.jsonl", val_rows)

    manifest = build_manifest(all_rows, added_rows)
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "summary.md").write_text(build_summary(all_rows, added_rows), encoding="utf-8")

    print(
        json.dumps(
            {
                "output_dir": str(OUTPUT_DIR),
                "train_total": len(train_rows),
                "val_total": len(val_rows),
                "added_contrastive_train_records": len(added_rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
