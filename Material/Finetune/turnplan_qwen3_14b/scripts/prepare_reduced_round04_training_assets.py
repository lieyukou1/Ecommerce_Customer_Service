from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATASET_ROOT = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1"
DEFAULT_INPUT_DIR = DATASET_ROOT / "reduced_round04_candidate_v1"


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
        from input_sanitizer import sanitize_record_input  # type: ignore
    finally:
        sys.path.pop(0)
    return str(SYSTEM_PROMPT), sanitize_record_input


def to_sft_record(record: dict, system_prompt: str, sanitize_record_input) -> dict:
    sanitized_input = sanitize_record_input(record["input"])
    return {
        "id": record["id"],
        "bucket": record["bucket"],
        "source": record["source"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(sanitized_input, ensure_ascii=False, indent=2)},
            {"role": "assistant", "content": json.dumps(record["output"], ensure_ascii=False, indent=2)},
        ],
        "meta": {
            "bucket": record["bucket"],
            "split": record["split"],
            "semantic_family": record.get("semantic_meta", {}).get("semantic_family"),
            "audit_meta": record.get("audit_meta"),
        },
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


def build_export_manifest(dataset_name: str, train_records: list[dict], val_records: list[dict]) -> dict:
    return {
        "dataset_name": dataset_name,
        "train_count": len(train_records),
        "val_count": len(val_records),
        "buckets": {
            "train": sorted({row["bucket"] for row in train_records}),
            "val": sorted({row["bucket"] for row in val_records}),
        },
        "source_files": {
            "train": "records_train.jsonl",
            "val": "records_val.jsonl",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export reduced round_04 candidate records to LLaMA-Factory assets.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--export-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir
    export_dir = args.export_dir or DATASET_ROOT / f"{input_dir.name}_exports_llm"
    dataset_name = input_dir.name

    train_records = read_jsonl(input_dir / "records_train.jsonl")
    val_records = read_jsonl(input_dir / "records_val.jsonl")
    system_prompt, sanitize_record_input = load_system_prompt()

    export_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(
        export_dir / "sft_train.jsonl",
        [to_sft_record(row, system_prompt, sanitize_record_input) for row in train_records],
    )
    write_jsonl(
        export_dir / "sft_val.jsonl",
        [to_sft_record(row, system_prompt, sanitize_record_input) for row in val_records],
    )
    (export_dir / "dataset_info.json").write_text(
        json.dumps(build_dataset_info(dataset_name), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (export_dir / "export_manifest.json").write_text(
        json.dumps(build_export_manifest(dataset_name, train_records, val_records), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "input_dir": str(input_dir),
                "export_dir": str(export_dir),
                "dataset_name": dataset_name,
                "train": len(train_records),
                "val": len(val_records),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
