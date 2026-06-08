from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from reduced_round04_contract import (
    BUCKET_CLASSIFICATION_RULES,
    CANONICAL_LLM_DIR,
    CATEGORY_BUCKET_REBUILD,
    CATEGORY_DESCRIPTIONS,
    CATEGORY_KEEP,
    CATEGORY_TARGETED_FIX,
    TARGETED_FIX_BUCKETS,
    TRIAGE_BUCKETS,
    TRIAGE_OUTPUT_DIR,
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


def classify_record(record: dict) -> str | None:
    bucket = record["bucket"]
    base_category = BUCKET_CLASSIFICATION_RULES.get(bucket)
    if base_category is None:
        return None
    if base_category == CATEGORY_KEEP and record["audit_meta"]["passed_for_sft"] is not True:
        return CATEGORY_TARGETED_FIX
    return base_category


def collect_records() -> list[dict]:
    train_rows = load_jsonl(CANONICAL_LLM_DIR / "records_train.jsonl")
    val_rows = load_jsonl(CANONICAL_LLM_DIR / "records_val.jsonl")
    rows = [row for row in train_rows + val_rows if row["bucket"] in TRIAGE_BUCKETS]
    return enrich_records(rows)


def build_manifest(grouped: dict[str, list[dict]]) -> dict:
    manifest: dict[str, dict] = {
        "dataset_id": TRIAGE_OUTPUT_DIR.name,
        "source_dataset": CANONICAL_LLM_DIR.name,
        "categories": {},
    }
    for category, rows in grouped.items():
        bucket_counts = defaultdict(lambda: {"train": 0, "val": 0, "sft_ready": 0, "not_ready": 0})
        note_counts: Counter[str] = Counter()
        for row in rows:
            bucket = row["bucket"]
            split = row["split"]
            bucket_counts[bucket][split] += 1
            if row["audit_meta"]["passed_for_sft"]:
                bucket_counts[bucket]["sft_ready"] += 1
            else:
                bucket_counts[bucket]["not_ready"] += 1
            for note in row["audit_meta"].get("audit_notes", []):
                note_counts[note] += 1
        manifest["categories"][category] = {
            "description": CATEGORY_DESCRIPTIONS[category],
            "total_records": len(rows),
            "bucket_counts": dict(bucket_counts),
            "record_ids": [row["id"] for row in rows],
            "top_audit_notes": note_counts.most_common(10),
        }
    return manifest


def build_summary(manifest: dict) -> str:
    lines = [
        "# reduced_round04_triage_v1 Summary",
        "",
        f"- source dataset: `{manifest['source_dataset']}`",
        "- purpose: classify reduced round_04 work into keep / targeted_fix / bucket_rebuild.",
        "",
    ]
    for category in (CATEGORY_KEEP, CATEGORY_TARGETED_FIX, CATEGORY_BUCKET_REBUILD):
        category_manifest = manifest["categories"].get(category, {})
        lines.extend(
            [
                f"## {category}",
                "",
                f"- description: {category_manifest.get('description', '')}",
                f"- total_records: `{category_manifest.get('total_records', 0)}`",
                "",
                "| bucket | train | val | sft_ready | not_ready |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for bucket, counts in sorted(category_manifest.get("bucket_counts", {}).items()):
            lines.append(
                f"| `{bucket}` | {counts['train']} | {counts['val']} | {counts['sft_ready']} | {counts['not_ready']} |"
            )
        if category == CATEGORY_TARGETED_FIX:
            lines.extend(
                [
                    "",
                    "Focused rationale:",
                    "",
                    "- `active_task_slot_fill` is audit-clean, but still remains a known regression-prone bucket in runtime replay.",
                ]
            )
        if category == CATEGORY_BUCKET_REBUILD:
            lines.extend(
                [
                    "",
                    "Focused rationale:",
                    "",
                    "- `ambiguous_all_null` still contains template residue and clarify-boundary noise.",
                    "- `directive_exit_runtime` still has timeline lead-in problems and should be rebuilt as a group.",
                ]
            )
        top_notes = category_manifest.get("top_audit_notes", [])
        if top_notes:
            lines.extend(["", "Top audit notes:", ""])
            for note, count in top_notes:
                lines.append(f"- `{note}`: `{count}`")
        lines.append("")
    lines.extend(
        [
            "## Notes",
            "",
            "- `work_order_read_only_task` is intentionally left out of this reduced training triage because high-loss read-only handling is currently absorbed by runtime compatibility logic.",
            f"- targeted-fix buckets: `{', '.join(TARGETED_FIX_BUCKETS)}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    rows = collect_records()
    grouped: dict[str, list[dict]] = {
        CATEGORY_KEEP: [],
        CATEGORY_TARGETED_FIX: [],
        CATEGORY_BUCKET_REBUILD: [],
    }
    for row in rows:
        category = classify_record(row)
        if category is None:
            continue
        grouped[category].append(row)

    TRIAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for category, category_rows in grouped.items():
        train_rows = [row for row in category_rows if row["split"] == "train"]
        val_rows = [row for row in category_rows if row["split"] == "val"]
        write_jsonl(TRIAGE_OUTPUT_DIR / f"{category}_train.jsonl", train_rows)
        write_jsonl(TRIAGE_OUTPUT_DIR / f"{category}_val.jsonl", val_rows)

    manifest = build_manifest(grouped)
    (TRIAGE_OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (TRIAGE_OUTPUT_DIR / "summary.md").write_text(build_summary(manifest), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_dir": str(TRIAGE_OUTPUT_DIR),
                "keep_total": len(grouped[CATEGORY_KEEP]),
                "targeted_fix_total": len(grouped[CATEGORY_TARGETED_FIX]),
                "bucket_rebuild_total": len(grouped[CATEGORY_BUCKET_REBUILD]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
