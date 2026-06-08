from __future__ import annotations

import json

from dataset_contract import BUCKET_SPECS, CANONICAL_DIR
from dataset_factory import build_split_records, signature_for_record


def write_jsonl(path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def assert_unique(records: list[dict], split: str) -> None:
    signatures = {}
    for record in records:
        signature = signature_for_record(record)
        if signature in signatures:
            raise ValueError(f"{split} duplicate pair detected: {record['id']} == {signatures[signature]}")
        signatures[signature] = record["id"]


def main() -> None:
    train_records = build_split_records("train", BUCKET_SPECS)
    val_records = build_split_records("val", BUCKET_SPECS)
    assert_unique(train_records, "train")
    assert_unique(val_records, "val")
    write_jsonl(CANONICAL_DIR / "records_train.jsonl", train_records)
    write_jsonl(CANONICAL_DIR / "records_val.jsonl", val_records)
    print(f"built train={len(train_records)} val={len(val_records)}")


if __name__ == "__main__":
    main()
