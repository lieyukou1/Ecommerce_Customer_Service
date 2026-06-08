from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_helpers import enrich_records
from dataset_contract import CANONICAL_DIR, REPORT_DIR, SYSTEM_PROMPT
from metrics import compute_metrics


def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_markdown(train_metrics: dict, val_metrics: dict, merged_metrics: dict) -> str:
    lines = [
        "# TurnPlan Phase 1 AI Audit",
        "",
        "## Overview",
        "",
        f"- train_records: {train_metrics['total_records']}",
        f"- val_records: {val_metrics['total_records']}",
        f"- total_records: {merged_metrics['total_records']}",
        f"- unique_input_label_pairs: {merged_metrics['unique_pairs']}",
        f"- duplicate_pairs: {merged_metrics['duplicate_pairs']}",
        f"- unique_user_messages: {merged_metrics['unique_user_messages']}",
        f"- unique_histories: {merged_metrics['unique_histories']}",
        "",
        "## Flow Coverage",
        "",
    ]
    for flow_id, count in merged_metrics["flow_counts"].items():
        lines.append(f"- `{flow_id}`: {count}")
    lines.extend(["", "## Knowledge Intent Coverage", ""])
    for intent_id, count in merged_metrics["knowledge_intent_counts"].items():
        lines.append(f"- `{intent_id}`: {count}")
    lines.extend(
        [
            "",
            "## Context Coverage",
            "",
            f"- active_task_records: {merged_metrics['active_task_records']}",
            f"- active_system_task_records: {merged_metrics['active_system_task_records']}",
            f"- paused_task_records: {merged_metrics['paused_task_records']}",
            f"- multi_slot_set_slots_records: {merged_metrics['multi_slot_set_slots_records']}",
            f"- contact_phone_slot_records: {merged_metrics['contact_phone_slot_records']}",
            f"- complaint_confirm_negative_records: {merged_metrics['complaint_confirm_negative_records']}",
            f"- conversation_state_distribution: `{json.dumps(merged_metrics['conversation_state_distribution'], ensure_ascii=False)}`",
            f"- history_length_distribution: `{json.dumps(merged_metrics['history_length_distribution'], ensure_ascii=False)}`",
            "",
            "## SFT Ready Audit",
            "",
            f"- sft_ready_pass_rate: {merged_metrics['sft_ready_pass_rate']:.4f}",
            f"- language_naturalness_pass_rate: {merged_metrics['language_naturalness_pass_rate']:.4f}",
            f"- history_state_consistency_pass_rate: {merged_metrics['history_state_consistency_pass_rate']:.4f}",
            f"- object_slot_consistency_pass_rate: {merged_metrics['object_slot_consistency_pass_rate']:.4f}",
            "",
            "## SFT Contract Checks",
            "",
            f"- mentions_intents_array: {merged_metrics['contract_flags']['mentions_intents_array']}",
            f"- mentions_flow_field: {merged_metrics['contract_flags']['mentions_flow_field']}",
            f"- mentions_active_system_task: {merged_metrics['contract_flags']['mentions_active_system_task']}",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AI audit reports for canonical TurnPlan records.")
    parser.add_argument("--input-dir", type=Path, default=CANONICAL_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_records = enrich_records(read_jsonl(args.input_dir / "records_train.jsonl"))
    val_records = enrich_records(read_jsonl(args.input_dir / "records_val.jsonl"))
    train_metrics = compute_metrics(train_records, SYSTEM_PROMPT)
    val_metrics = compute_metrics(val_records, SYSTEM_PROMPT)
    merged_metrics = compute_metrics(train_records + val_records, SYSTEM_PROMPT)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (args.report_dir / "ai_audit.json").write_text(
        json.dumps(
            {"train": train_metrics, "val": val_metrics, "all": merged_metrics},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_text(args.report_dir / "ai_audit.md", render_markdown(train_metrics, val_metrics, merged_metrics))
    print(
        json.dumps(
            {
                "input_dir": str(args.input_dir),
                "report_json": str(args.report_dir / "ai_audit.json"),
                "report_md": str(args.report_dir / "ai_audit.md"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
