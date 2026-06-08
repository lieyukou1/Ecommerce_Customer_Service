from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1"
DEFAULT_INPUT_DIR = DATASET_ROOT / "reduced_round03_aug_v1"
DEFAULT_OUTPUT_DIR = DATASET_ROOT / "reduced_round03_curated_v1"

DROP_IDS = {
    "tp_active_task_slot_fill_train_016",
    "tp_active_task_slot_fill_train_044",
    "tp_r3_active_task_slot_fill_train_079",
    "tp_r3_active_task_slot_fill_train_056",
    "tp_r3_active_task_slot_fill_train_064",
    "tp_r3_active_task_slot_fill_train_076",
    "tp_r3_active_task_slot_fill_train_078",
    "tp_r3_task_interrupt_resume_cancel_train_047",
    "tp_r3_task_interrupt_resume_cancel_train_054",
    "tp_r3_task_interrupt_resume_cancel_train_060",
    "tp_r3_task_interrupt_resume_cancel_train_064",
    "tp_r3_task_interrupt_resume_cancel_train_069",
    "tp_r3_task_interrupt_resume_cancel_train_076",
    "tp_r3_work_order_business_urge_val_005",
    "tp_r3_work_order_business_urge_val_007",
}

PATCHES = {
    "tp_directive_exit_runtime_train_007": {
        "user_message": "这事先放一放吧，咱们换个别的说。"
    },
    "tp_active_task_slot_fill_train_023": {
        "user_message": "行，那就按投诉提吧。"
    },
    "tp_active_task_slot_fill_train_035": {
        "user_message": "老人现在最怕热，这窗帘一直卡着，屋里闷得不行。"
    },
    "tp_active_task_slot_fill_val_009": {
        "user_message": "现在出入都不方便，真的挺碍事的。"
    },
    "tp_r3_active_task_slot_fill_train_054": {
        "user_message": "打 13800000025 就行。"
    },
    "tp_r3_active_task_slot_fill_train_055": {
        "user_message": "那就说说物业服务都管哪些吧。"
    },
    "tp_r3_active_task_slot_fill_train_060": {
        "user_message": "打 13800000032 这个号。"
    },
    "tp_r3_active_task_slot_fill_train_066": {
        "user_message": "留 13800000031 吧。"
    },
    "tp_r3_active_task_slot_fill_train_070": {
        "user_message": "用 13800000045 联系我。"
    },
    "tp_r3_active_task_slot_fill_val_013": {
        "user_message": "打 13800001004 就行。"
    },
}

TARGET_BUCKETS = {
    "ambiguous_all_null": {"train": 80, "val": 20},
    "active_task_slot_fill": {"train": 80, "val": 20},
    "task_interrupt_resume_cancel": {"train": 80, "val": 20},
    "directive_exit_runtime": {"train": 40, "val": 10},
    "work_order_business_urge": {"train": 30, "val": 8},
    "work_order_business_complaint": {"train": 30, "val": 8},
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def apply_patch_to_record(record: dict) -> dict:
    patch = PATCHES.get(record["id"])
    if not patch:
        return record
    cloned = json.loads(json.dumps(record, ensure_ascii=False))
    if "history" in patch:
        cloned["input"]["history"] = patch["history"]
    if "user_message" in patch:
        cloned["input"]["user_message"] = patch["user_message"]
    meta = dict(cloned["meta"])
    curation_notes = list(meta.get("curation_notes", []))
    curation_notes.append("manual_patch_v1")
    meta["curation_notes"] = curation_notes
    cloned["meta"] = meta
    return cloned


def build_summary(rows: list[dict], dropped: list[str], patched: list[str]) -> str:
    counts = defaultdict(lambda: {"train": 0, "val": 0})
    for row in rows:
        counts[row["bucket"]][row["split"]] += 1

    lines = [
        "# reduced_round03_curated_v1 Summary",
        "",
        "- source dataset: `reduced_round03_aug_v1`",
        "- purpose: remove wrong-bucket / slot-drift outliers before round_03 training",
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
            f"- dropped_records: `{len(dropped)}`",
            f"- patched_records: `{len(patched)}`",
            "",
            "## Dropped IDs",
            "",
        ]
    )
    for record_id in dropped:
        lines.append(f"- `{record_id}`")
    lines.extend(["", "## Patched IDs", ""])
    for record_id in patched:
        lines.append(f"- `{record_id}`")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Curate reduced round_03 dataset by dropping and patching known outliers.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_rows = read_jsonl(args.input_dir / "records_train.jsonl")
    val_rows = read_jsonl(args.input_dir / "records_val.jsonl")
    all_rows = train_rows + val_rows

    curated_rows: list[dict] = []
    dropped: list[str] = []
    patched: list[str] = []
    seen_ids: set[str] = set()

    for row in all_rows:
        record_id = row["id"]
        if record_id in DROP_IDS:
            dropped.append(record_id)
            continue
        curated = apply_patch_to_record(row)
        if curated["id"] in PATCHES:
            patched.append(curated["id"])
        if curated["id"] in seen_ids:
            raise ValueError(f"duplicate id after curation: {curated['id']}")
        seen_ids.add(curated["id"])
        curated_rows.append(curated)

    curated_train = [row for row in curated_rows if row["split"] == "train"]
    curated_val = [row for row in curated_rows if row["split"] == "val"]
    write_jsonl(args.output_dir / "records_train.jsonl", curated_train)
    write_jsonl(args.output_dir / "records_val.jsonl", curated_val)

    manifest = {
        "dataset_id": args.output_dir.name,
        "source_dataset": args.input_dir.name,
        "train_total": len(curated_train),
        "val_total": len(curated_val),
        "bucket_counts": {
            bucket: {
                "train": sum(1 for row in curated_train if row["bucket"] == bucket),
                "val": sum(1 for row in curated_val if row["bucket"] == bucket),
            }
            for bucket in TARGET_BUCKETS
        },
        "dropped_ids": dropped,
        "patched_ids": patched,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (args.output_dir / "summary.md").write_text(
        build_summary(curated_rows, dropped, patched),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output_dir": str(args.output_dir),
                "train_total": len(curated_train),
                "val_total": len(curated_val),
                "dropped": len(dropped),
                "patched": len(patched),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
