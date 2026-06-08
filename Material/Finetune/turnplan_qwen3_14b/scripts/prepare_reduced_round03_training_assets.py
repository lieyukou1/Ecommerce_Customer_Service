from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1"
DEFAULT_INPUT_DIR = DATASET_ROOT / "reduced_round03_base_v1"
DEFAULT_TARGET_BUCKETS = {
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


def load_system_prompt() -> str:
    scripts_dir = DATASET_ROOT / "scripts"
    sys.path.insert(0, str(scripts_dir))
    try:
        from dataset_contract import SYSTEM_PROMPT  # type: ignore
    finally:
        sys.path.pop(0)
    return str(SYSTEM_PROMPT)


def to_sft_record(record: dict, system_prompt: str) -> dict:
    return {
        "id": record["id"],
        "bucket": record["bucket"],
        "source": record["source"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(record["input"], ensure_ascii=False, indent=2)},
            {"role": "assistant", "content": json.dumps(record["output"], ensure_ascii=False, indent=2)},
        ],
        "meta": record["meta"],
    }


def build_dataset_info(dataset_name: str) -> dict:
    tags = {
        "role_tag": "role",
        "content_tag": "content",
        "user_tag": "user",
        "assistant_tag": "assistant",
        "system_tag": "system",
    }
    return {
        f"{dataset_name}_train": {
            "file_name": "sft_train.jsonl",
            "formatting": "sharegpt",
            "columns": {"messages": "messages"},
            "tags": tags,
        },
        f"{dataset_name}_val": {
            "file_name": "sft_val.jsonl",
            "formatting": "sharegpt",
            "columns": {"messages": "messages"},
            "tags": tags,
        },
    }


def build_gap_report(manifest: dict) -> dict:
    target_buckets = manifest.get("target_buckets", DEFAULT_TARGET_BUCKETS)
    gap_by_bucket: dict[str, dict[str, int]] = {}
    for bucket, actual in manifest["bucket_counts"].items():
        target = target_buckets[bucket]
        gap_by_bucket[bucket] = {
            "train_actual": actual["train"],
            "train_target": target["train"],
            "train_gap": max(0, target["train"] - actual["train"]),
            "val_actual": actual["val"],
            "val_target": target["val"],
            "val_gap": max(0, target["val"] - actual["val"]),
        }
    return {
        "dataset_id": manifest["dataset_id"],
        "source_dataset": manifest["source_dataset"],
        "target_buckets": target_buckets,
        "gap_by_bucket": gap_by_bucket,
    }


def build_gap_markdown(dataset_name: str, gap_report: dict) -> str:
    lines = [
        f"# {dataset_name} Augmentation Gaps",
        "",
        "- purpose: targeted augmentation todo after base slice extraction",
        "",
        "| bucket | train_actual | train_target | train_gap | val_actual | val_target | val_gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for bucket, payload in gap_report["gap_by_bucket"].items():
        lines.append(
            f"| `{bucket}` | {payload['train_actual']} | {payload['train_target']} | {payload['train_gap']} | "
            f"{payload['val_actual']} | {payload['val_target']} | {payload['val_gap']} |"
        )

    lines.extend(
        [
            "",
            "## Priority",
            "",
            "1. `ambiguous_all_null`",
            "2. `task_interrupt_resume_cancel`",
            "3. `active_task_slot_fill`",
            "4. `directive_exit_runtime`",
            "5. `work_order_business_urge` / `work_order_business_complaint` val-only 补齐",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export reduced round_03 canonical records to SFT assets.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--export-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir
    export_dir = args.export_dir or DATASET_ROOT / f"{input_dir.name}_exports_llm"
    manifest_path = input_dir / "manifest.json"
    dataset_name = input_dir.name

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    train_records = read_jsonl(input_dir / "records_train.jsonl")
    val_records = read_jsonl(input_dir / "records_val.jsonl")
    system_prompt = load_system_prompt()

    export_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(export_dir / "sft_train.jsonl", [to_sft_record(row, system_prompt) for row in train_records])
    write_jsonl(export_dir / "sft_val.jsonl", [to_sft_record(row, system_prompt) for row in val_records])
    (export_dir / "dataset_info.json").write_text(
        json.dumps(build_dataset_info(dataset_name), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    gap_report = build_gap_report(manifest)
    (input_dir / "augmentation_gaps.json").write_text(
        json.dumps(gap_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (input_dir / "augmentation_plan.md").write_text(
        build_gap_markdown(dataset_name, gap_report),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "input_dir": str(input_dir),
                "export_dir": str(export_dir),
                "train": len(train_records),
                "val": len(val_records),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
