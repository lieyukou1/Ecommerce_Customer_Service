from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_helpers import enrich_records
from dataset_contract import CANONICAL_DIR, EXPORT_DIR, SYSTEM_PROMPT
from input_sanitizer import sanitize_record_input


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def to_sft_record(record: dict) -> dict:
    sanitized_input = sanitize_record_input(record["input"])
    return {
        "id": record["id"],
        "bucket": record["bucket"],
        "source": record["source"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(sanitized_input, ensure_ascii=False, indent=2)},
            {"role": "assistant", "content": json.dumps(record["output"], ensure_ascii=False, indent=2)},
        ],
        "meta": {
            **record["meta"],
            "semantic_meta": record.get("semantic_meta"),
            "audit_meta": record.get("audit_meta"),
        },
    }


def filter_sft_ready(records: list[dict], allow_unsafe: bool) -> list[dict]:
    if allow_unsafe:
        return records
    return [record for record in records if record.get("audit_meta", {}).get("passed_for_sft") is True]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export canonical TurnPlan records to SFT jsonl.")
    parser.add_argument("--input-dir", type=Path, default=CANONICAL_DIR)
    parser.add_argument("--output-dir", type=Path, default=EXPORT_DIR)
    parser.add_argument("--allow-unsafe", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_records = enrich_records(read_jsonl(args.input_dir / "records_train.jsonl"))
    val_records = enrich_records(read_jsonl(args.input_dir / "records_val.jsonl"))
    safe_train = filter_sft_ready(train_records, args.allow_unsafe)
    safe_val = filter_sft_ready(val_records, args.allow_unsafe)
    write_jsonl(args.output_dir / "sft_train.jsonl", [to_sft_record(record) for record in safe_train])
    write_jsonl(args.output_dir / "sft_val.jsonl", [to_sft_record(record) for record in safe_val])
    print(
        json.dumps(
            {
                "input_dir": str(args.input_dir),
                "output_dir": str(args.output_dir),
                "train": len(safe_train),
                "val": len(safe_val),
                "allow_unsafe": args.allow_unsafe,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
