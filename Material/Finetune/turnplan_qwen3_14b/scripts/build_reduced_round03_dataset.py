from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
CANONICAL_DIR = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1" / "canonical_llm"
OUTPUT_DIR = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1" / "reduced_round03_base_v1"

SELECTED_BUCKETS = [
    "ambiguous_all_null",
    "active_task_slot_fill",
    "task_interrupt_resume_cancel",
    "directive_exit_runtime",
    "work_order_business_urge",
    "work_order_business_complaint",
]
EXCLUDED_BUCKETS = [
    "work_order_read_only_task",
    "service_item_knowledge",
    "object_context_followup",
    "chitchat",
]
TARGET_BUCKETS = {
    "ambiguous_all_null": {"train": 80, "val": 20},
    "active_task_slot_fill": {"train": 80, "val": 20},
    "task_interrupt_resume_cancel": {"train": 80, "val": 20},
    "directive_exit_runtime": {"train": 40, "val": 10},
    "work_order_business_urge": {"train": 30, "val": 8},
    "work_order_business_complaint": {"train": 30, "val": 8},
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def validate_row(row: dict) -> list[str]:
    errors: list[str] = []
    bucket = row["bucket"]
    output = row["output"]
    track_count = sum(1 for value in output.values() if value is not None)

    if bucket == "active_task_slot_fill":
        if not (row["input"].get("active_task") or row["input"].get("active_system_task")):
            errors.append("active_task_slot_fill missing active runtime context")

    if bucket == "ambiguous_all_null":
        if track_count != 0:
            errors.append("ambiguous_all_null must be all-null")

    if bucket == "directive_exit_runtime":
        directive = output.get("directive")
        if directive != {"action": "exit_runtime"}:
            errors.append("directive_exit_runtime must equal exit_runtime")

    if bucket in {"work_order_business_urge", "work_order_business_complaint", "task_interrupt_resume_cancel"}:
        if output.get("task") is None:
            errors.append(f"{bucket} must keep task output")

    return errors


def build_summary(manifest: dict) -> str:
    lines = [
        "# reduced_round03_base_v1 Summary",
        "",
        "- source: `turnplan-phase1 / canonical_llm`",
        "- purpose: reduced `round_03` base slice before targeted augmentation",
        "",
        "## Selected Buckets",
        "",
    ]
    for bucket in SELECTED_BUCKETS:
        lines.append(f"- `{bucket}`")

    lines.extend(
        [
            "",
            "## Excluded Buckets",
            "",
        ]
    )
    for bucket in EXCLUDED_BUCKETS:
        lines.append(f"- `{bucket}`")

    lines.extend(
        [
            "",
            "## Counts",
            "",
            "| bucket | train_actual | train_target | val_actual | val_target |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for bucket in SELECTED_BUCKETS:
        actual = manifest["bucket_counts"][bucket]
        target = TARGET_BUCKETS[bucket]
        lines.append(
            f"| `{bucket}` | {actual['train']} | {target['train']} | {actual['val']} | {target['val']} |"
        )

    lines.extend(
        [
            "",
            f"- train_total: `{manifest['train_total']}`",
            f"- val_total: `{manifest['val_total']}`",
            "",
            "## Validation",
            "",
            f"- checked_records: `{manifest['validated_records']}`",
            f"- validation_errors: `{manifest['validation_error_count']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    train_rows = load_jsonl(CANONICAL_DIR / "records_train.jsonl")
    val_rows = load_jsonl(CANONICAL_DIR / "records_val.jsonl")

    reduced_train = [row for row in train_rows if row["bucket"] in SELECTED_BUCKETS]
    reduced_val = [row for row in val_rows if row["bucket"] in SELECTED_BUCKETS]

    validation_errors: list[dict] = []
    for split, rows in (("train", reduced_train), ("val", reduced_val)):
        for row in rows:
            for error in validate_row(row):
                validation_errors.append({"split": split, "id": row["id"], "bucket": row["bucket"], "error": error})

    if validation_errors:
        raise SystemExit(json.dumps(validation_errors[:20], ensure_ascii=False, indent=2))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dump_jsonl(OUTPUT_DIR / "records_train.jsonl", reduced_train)
    dump_jsonl(OUTPUT_DIR / "records_val.jsonl", reduced_val)

    train_counter = Counter(row["bucket"] for row in reduced_train)
    val_counter = Counter(row["bucket"] for row in reduced_val)
    manifest = {
        "dataset_id": "reduced_round03_base_v1",
        "source_dataset": "turnplan-phase1/canonical_llm",
        "selected_buckets": SELECTED_BUCKETS,
        "excluded_buckets": EXCLUDED_BUCKETS,
        "target_buckets": TARGET_BUCKETS,
        "train_total": len(reduced_train),
        "val_total": len(reduced_val),
        "validated_records": len(reduced_train) + len(reduced_val),
        "validation_error_count": len(validation_errors),
        "bucket_counts": {
            bucket: {"train": train_counter.get(bucket, 0), "val": val_counter.get(bucket, 0)}
            for bucket in SELECTED_BUCKETS
        },
        "train_ids": [row["id"] for row in reduced_train],
        "val_ids": [row["id"] for row in reduced_val],
    }
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "summary.md").write_text(build_summary(manifest), encoding="utf-8")
    print(json.dumps({"output_dir": str(OUTPUT_DIR), "train_total": len(reduced_train), "val_total": len(reduced_val)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
