from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
REPORT_ROOT = REPO_ROOT / "Material" / "Finetune" / "turnplan_qwen3_14b"
DATASET_ROOT = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1"

BASE_PREDICTIONS = (
    REPORT_ROOT
    / "reports"
    / "runtime_eval_reduced"
    / "qwen3_14b_base_reduced_round04_val_nothinking"
    / "predictions.jsonl"
)
CANDIDATE_PREDICTIONS = (
    REPORT_ROOT
    / "reports"
    / "runtime_eval_reduced"
    / "qwen3_14b_turnplan_r5reduced_20260607a_val_nothinking"
    / "predictions.jsonl"
)
VAL_RECORDS = DATASET_ROOT / "reduced_round04_candidate_v1" / "records_val.jsonl"
OUTPUT_DIR = REPORT_ROOT / "rounds" / "round_05" / "artifacts"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def is_effective_success(row: dict) -> bool:
    return bool(row["track_match"] and row["json_valid"] and row["effective_gate_pass"])


def build_row(base_row: dict, candidate_row: dict, record: dict) -> dict:
    return {
        "id": base_row["id"],
        "bucket": base_row["bucket"],
        "user_message": record["input"]["user_message"],
        "gold_output": base_row["gold_output"],
        "base_predicted_output": base_row["predicted_output"],
        "candidate_predicted_output": candidate_row["predicted_output"],
        "base_track": base_row["pred_track"],
        "candidate_track": candidate_row["pred_track"],
        "base_success": is_effective_success(base_row),
        "candidate_success": is_effective_success(candidate_row),
        "base_track_match": base_row["track_match"],
        "candidate_track_match": candidate_row["track_match"],
        "base_command_family_match": base_row["command_family_match"],
        "candidate_command_family_match": candidate_row["command_family_match"],
        "base_flow_match": base_row["flow_match"],
        "candidate_flow_match": candidate_row["flow_match"],
        "base_slot_match": base_row["slot_match"],
        "candidate_slot_match": candidate_row["slot_match"],
        "base_effective_gate_pass": base_row["effective_gate_pass"],
        "candidate_effective_gate_pass": candidate_row["effective_gate_pass"],
        "base_protocol_gate_pass": base_row["protocol_gate_accepted"],
        "candidate_protocol_gate_pass": candidate_row["protocol_gate_accepted"],
    }


def classify_change(row: dict) -> str:
    if row["base_success"] and not row["candidate_success"]:
        if row["candidate_track"] == "all_null":
            return "task_to_all_null_regression"
        if row["candidate_track"] == "directive":
            return "task_to_exit_runtime_regression"
        return "other_regression"
    if (not row["base_success"]) and row["candidate_success"]:
        if row["candidate_track"] == "all_null":
            return "all_null_gain"
        return "other_gain"
    if row["base_command_family_match"] != row["candidate_command_family_match"]:
        return "command_family_shift_without_net_success_change"
    if row["base_flow_match"] != row["candidate_flow_match"]:
        return "flow_shift_without_net_success_change"
    if row["base_slot_match"] != row["candidate_slot_match"]:
        return "slot_extraction_change_without_net_success_change"
    return "unchanged"


def build_markdown(rows: list[dict]) -> str:
    regressions = [row for row in rows if row["change_family"] in {"task_to_all_null_regression", "task_to_exit_runtime_regression", "other_regression"}]
    gains = [row for row in rows if row["change_family"] in {"all_null_gain", "other_gain"}]
    non_net_changes = [
        row
        for row in rows
        if row["change_family"] not in {"unchanged", "task_to_all_null_regression", "task_to_exit_runtime_regression", "other_regression", "all_null_gain", "other_gain"}
    ]

    lines = [
        "# round_05 Base vs Candidate Regression Analysis",
        "",
        "## Summary",
        "",
        f"- total compared samples: `{len(rows)}`",
        f"- effective regressions: `{len(regressions)}`",
        f"- effective gains: `{len(gains)}`",
        f"- non-net-output changes: `{len(non_net_changes)}`",
        "",
        "## Change Family Counts",
        "",
    ]

    family_counts = Counter(row["change_family"] for row in rows if row["change_family"] != "unchanged")
    for family, count in sorted(family_counts.items()):
        lines.append(f"- `{family}`: `{count}`")

    lines.extend(["", "## Regressions", ""])
    for row in regressions:
        lines.extend(
            [
                f"### {row['id']}",
                f"- bucket: `{row['bucket']}`",
                f"- user_message: `{row['user_message']}`",
                f"- change_family: `{row['change_family']}`",
                f"- base_track -> candidate_track: `{row['base_track']} -> {row['candidate_track']}`",
                f"- command_family_match: `{row['base_command_family_match']} -> {row['candidate_command_family_match']}`",
                f"- flow_match: `{row['base_flow_match']} -> {row['candidate_flow_match']}`",
                f"- effective_gate_pass: `{row['base_effective_gate_pass']} -> {row['candidate_effective_gate_pass']}`",
                f"- gold: `{json.dumps(row['gold_output'], ensure_ascii=False)}`",
                f"- base: `{json.dumps(row['base_predicted_output'], ensure_ascii=False)}`",
                f"- candidate: `{json.dumps(row['candidate_predicted_output'], ensure_ascii=False)}`",
                "",
            ]
        )

    lines.extend(["## Gains", ""])
    for row in gains:
        lines.extend(
            [
                f"### {row['id']}",
                f"- bucket: `{row['bucket']}`",
                f"- user_message: `{row['user_message']}`",
                f"- change_family: `{row['change_family']}`",
                f"- base_track -> candidate_track: `{row['base_track']} -> {row['candidate_track']}`",
                f"- gold: `{json.dumps(row['gold_output'], ensure_ascii=False)}`",
                f"- base: `{json.dumps(row['base_predicted_output'], ensure_ascii=False)}`",
                f"- candidate: `{json.dumps(row['candidate_predicted_output'], ensure_ascii=False)}`",
                "",
            ]
        )

    lines.extend(["## Non-Net Changes", ""])
    for row in non_net_changes:
        lines.extend(
            [
                f"### {row['id']}",
                f"- bucket: `{row['bucket']}`",
                f"- user_message: `{row['user_message']}`",
                f"- change_family: `{row['change_family']}`",
                f"- command_family_match: `{row['base_command_family_match']} -> {row['candidate_command_family_match']}`",
                f"- flow_match: `{row['base_flow_match']} -> {row['candidate_flow_match']}`",
                f"- slot_match: `{row['base_slot_match']} -> {row['candidate_slot_match']}`",
                "",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    base_rows = {row["id"]: row for row in load_jsonl(BASE_PREDICTIONS)}
    candidate_rows = {row["id"]: row for row in load_jsonl(CANDIDATE_PREDICTIONS)}
    val_records = {row["id"]: row for row in load_jsonl(VAL_RECORDS)}

    merged_rows: list[dict] = []
    for row_id, base_row in base_rows.items():
        candidate_row = candidate_rows[row_id]
        record = val_records[row_id]
        merged = build_row(base_row, candidate_row, record)
        merged["change_family"] = classify_change(merged)
        merged_rows.append(merged)

    merged_rows.sort(key=lambda item: (item["change_family"], item["bucket"], item["id"]))

    summary = {
        "total": len(merged_rows),
        "regressions": sum(
            1
            for row in merged_rows
            if row["change_family"] in {"task_to_all_null_regression", "task_to_exit_runtime_regression", "other_regression"}
        ),
        "gains": sum(1 for row in merged_rows if row["change_family"] in {"all_null_gain", "other_gain"}),
        "change_family_counts": Counter(row["change_family"] for row in merged_rows if row["change_family"] != "unchanged"),
        "regression_bucket_counts": Counter(
            row["bucket"]
            for row in merged_rows
            if row["change_family"] in {"task_to_all_null_regression", "task_to_exit_runtime_regression", "other_regression"}
        ),
        "gain_bucket_counts": Counter(
            row["bucket"]
            for row in merged_rows
            if row["change_family"] in {"all_null_gain", "other_gain"}
        ),
    }

    (OUTPUT_DIR / "round05_base_vs_candidate_regressions.json").write_text(
        json.dumps({"summary": summary, "rows": merged_rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "round05_base_vs_candidate_regressions.md").write_text(
        build_markdown(merged_rows),
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2, default=lambda x: dict(x)))


if __name__ == "__main__":
    main()
