from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from reduced_round04_contract import (
    CANONICAL_LLM_DIR,
    CATEGORY_KEEP,
    KEEP_BASE_OUTPUT_DIR,
    KEEP_BUCKETS,
    DATASET_SCRIPTS_DIR,
)

sys.path.insert(0, str(DATASET_SCRIPTS_DIR))

from audit_helpers import enrich_records  # noqa: E402


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def collect_keep_rows() -> list[dict]:
    train_rows = load_jsonl(CANONICAL_LLM_DIR / "records_train.jsonl")
    val_rows = load_jsonl(CANONICAL_LLM_DIR / "records_val.jsonl")
    rows = [row for row in train_rows + val_rows if row["bucket"] in KEEP_BUCKETS]
    rows = enrich_records(rows)
    return [row for row in rows if row["audit_meta"]["passed_for_sft"] is True]


def build_manifest(rows: list[dict]) -> dict:
    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "val"]
    train_counter = Counter(row["bucket"] for row in train_rows)
    val_counter = Counter(row["bucket"] for row in val_rows)
    return {
        "dataset_id": KEEP_BASE_OUTPUT_DIR.name,
        "source_dataset": CANONICAL_LLM_DIR.name,
        "category": CATEGORY_KEEP,
        "train_total": len(train_rows),
        "val_total": len(val_rows),
        "bucket_counts": {
            bucket: {"train": train_counter.get(bucket, 0), "val": val_counter.get(bucket, 0)}
            for bucket in KEEP_BUCKETS
        },
        "train_ids": [row["id"] for row in train_rows],
        "val_ids": [row["id"] for row in val_rows],
    }


def build_summary(manifest: dict) -> str:
    lines = [
        "# reduced_round04_keep_base_v1 Summary",
        "",
        f"- source dataset: `{manifest['source_dataset']}`",
        "- purpose: keep-only reduced base after audit gating, before targeted repair and bucket rebuild are added back.",
        "",
        "| bucket | train | val |",
        "| --- | ---: | ---: |",
    ]
    for bucket, counts in manifest["bucket_counts"].items():
        lines.append(f"| `{bucket}` | {counts['train']} | {counts['val']} |")
    lines.extend(
        [
            "",
            f"- train_total: `{manifest['train_total']}`",
            f"- val_total: `{manifest['val_total']}`",
            "",
            "Excluded on purpose:",
            "",
            "- `active_task_slot_fill`: moved to targeted-fix queue",
            "- `ambiguous_all_null`: moved to bucket-rebuild queue",
            "- `directive_exit_runtime`: moved to bucket-rebuild queue",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    rows = collect_keep_rows()
    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "val"]
    KEEP_BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(KEEP_BASE_OUTPUT_DIR / "records_train.jsonl", train_rows)
    write_jsonl(KEEP_BASE_OUTPUT_DIR / "records_val.jsonl", val_rows)
    manifest = build_manifest(rows)
    (KEEP_BASE_OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (KEEP_BASE_OUTPUT_DIR / "summary.md").write_text(build_summary(manifest), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_dir": str(KEEP_BASE_OUTPUT_DIR),
                "train_total": len(train_rows),
                "val_total": len(val_rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
