from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_helpers import enrich_records
from dataset_contract import (
    ALLOWED_INPUT_KEYS,
    ALLOWED_OUTPUT_KEYS,
    ALLOWED_TASK_COMMANDS,
    ALLOWED_TOP_LEVEL_KEYS,
    BUCKET_SPECS,
    CANONICAL_DIR,
    FLOW_MIN_COUNTS,
    INTENT_MIN_COUNTS,
    REQUIRED_TOP_LEVEL_KEYS,
    SEMANTIC_FAMILIES,
)
from metrics import active_track, compute_metrics


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def validate_record(record: dict) -> None:
    record_id = record.get("id", "<unknown>")
    keys = set(record.keys())
    if not REQUIRED_TOP_LEVEL_KEYS.issubset(keys):
        raise ValueError(f"{record_id} missing required top-level keys")
    if not keys.issubset(ALLOWED_TOP_LEVEL_KEYS):
        raise ValueError(f"{record_id} top-level keys mismatch")

    if set(record["input"].keys()) != ALLOWED_INPUT_KEYS:
        raise ValueError(f"{record_id} input keys mismatch")
    if set(record["output"].keys()) != ALLOWED_OUTPUT_KEYS:
        raise ValueError(f"{record_id} output keys mismatch")

    track = active_track(record["output"])
    if track == "multiple":
        raise ValueError(f"{record_id} has multiple active tracks")
    if record["meta"]["primary_track"] != track:
        raise ValueError(f"{record_id} primary_track mismatch")

    directive = record["output"]["directive"]
    if directive is not None and directive.get("action") != "exit_runtime":
        raise ValueError(f"{record_id} invalid directive action")

    task_payload = record["output"]["task"]
    if task_payload is not None:
        for command in task_payload.get("commands", []):
            if command.get("command") not in ALLOWED_TASK_COMMANDS:
                raise ValueError(f"{record_id} invalid task command")

    semantic_meta = record.get("semantic_meta")
    if semantic_meta is not None:
        family = semantic_meta.get("semantic_family")
        if family is not None and family not in SEMANTIC_FAMILIES:
            raise ValueError(f"{record_id} invalid semantic_family")

    audit_meta = record.get("audit_meta")
    if audit_meta is not None and "passed_for_sft" not in audit_meta:
        raise ValueError(f"{record_id} audit_meta missing passed_for_sft")


def validate_counts(records: list[dict], split: str) -> None:
    counts = {bucket: 0 for bucket in BUCKET_SPECS}
    for record in records:
        counts[record["bucket"]] += 1
    for bucket, expected in BUCKET_SPECS.items():
        if counts[bucket] != expected[split]:
            raise ValueError(
                f"{split} bucket {bucket} count mismatch: {counts[bucket]} != {expected[split]}"
            )


def validate_metrics(metrics: dict, val_metrics: dict, total_records: int) -> None:
    if metrics["duplicate_pairs"] != 0:
        raise ValueError("exact duplicate input+label pairs detected")
    if metrics["unique_histories"] < 80:
        raise ValueError("history variety too low")
    if 0 not in metrics["history_length_distribution"]:
        raise ValueError("cold-start history missing")
    if not any(length >= 6 for length in metrics["history_length_distribution"]):
        raise ValueError("6-turn-or-longer history missing")
    if metrics["active_system_task_records"] < 25:
        raise ValueError("active_system_task coverage too low")
    if metrics["paused_task_records"] < 10:
        raise ValueError("paused_tasks coverage too low")
    if metrics["multi_slot_set_slots_records"] < 20:
        raise ValueError("multi-slot set_slots coverage too low")
    if metrics["contact_phone_slot_records"] < 12:
        raise ValueError("contact_phone slot coverage too low")
    if metrics["complaint_confirm_negative_records"] < 6:
        raise ValueError("complaint_confirm negative coverage too low")
    if len(metrics["conversation_state_distribution"]) < 4:
        raise ValueError("conversation_state variety too low")
    if val_metrics["history_length_distribution"].get(0, 0) == 0:
        raise ValueError("validation split missing cold-start cases")

    for flow_id, minimum in FLOW_MIN_COUNTS.items():
        if metrics["flow_counts"][flow_id] < minimum:
            raise ValueError(f"flow coverage too low for {flow_id}")
    for intent_id, minimum in INTENT_MIN_COUNTS.items():
        if metrics["knowledge_intent_counts"][intent_id] < minimum:
            raise ValueError(f"knowledge intent coverage too low for {intent_id}")

    if metrics["unique_user_messages"] / total_records < 0.85:
        raise ValueError("user_message uniqueness ratio too low")
    if metrics["sft_ready_pass_rate"] == 0:
        raise ValueError("no SFT-ready samples detected")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate canonical TurnPlan records.")
    parser.add_argument("--input-dir", type=Path, default=CANONICAL_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_records = enrich_records(read_jsonl(args.input_dir / "records_train.jsonl"))
    val_records = enrich_records(read_jsonl(args.input_dir / "records_val.jsonl"))
    for record in train_records + val_records:
        validate_record(record)
    validate_counts(train_records, "train")
    validate_counts(val_records, "val")
    all_metrics = compute_metrics(train_records + val_records)
    val_metrics = compute_metrics(val_records)
    validate_metrics(all_metrics, val_metrics, len(train_records) + len(val_records))
    print(
        json.dumps(
            {
                "input_dir": str(args.input_dir),
                "train": len(train_records),
                "val": len(val_records),
                "status": "ok",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
