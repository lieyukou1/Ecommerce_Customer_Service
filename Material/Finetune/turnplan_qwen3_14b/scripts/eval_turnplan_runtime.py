from __future__ import annotations

import argparse
import asyncio
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from common_runtime import (
    REPO_ROOT,
    active_track,
    build_bucket_metrics,
    build_state_from_input,
    extract_command_names,
    extract_flow_sequence,
    extract_merged_slots,
    load_flows_and_intents,
    load_records,
    parse_json_text,
    turnplan_to_dict,
)

from atguigu.infrastructure.llm import llm
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.protocol_gate import TurnProtocolGate
from atguigu.plan.turn_plan import TurnPlan
from atguigu.plan.turn_validator import TurnPlanValidator
from atguigu.prompt.loader import load_prompt


DEFAULT_CANONICAL_DIR = REPO_ROOT / "Material" / "Datasets" / "turnplan-phase1" / "canonical_llm"
HIGH_LOSS_READ_ONLY_FLOW_IDS = {
    "resident_work_orders_list_query",
    "resident_service_items_list_query",
    "work_order_status_query",
    "service_progress_tracking",
    "service_item_detail_query",
}
WORK_ORDER_RUNTIME_FLOW_IDS = {
    "work_order_status_query",
    "service_progress_tracking",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate TurnPlan with the real project prompt and protocol gate.")
    parser.add_argument("--canonical-dir", type=Path, default=DEFAULT_CANONICAL_DIR)
    parser.add_argument("--split", choices=["train", "val"], default="val")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--label", default="unnamed")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--concurrency", type=int, default=4)
    return parser.parse_args()


async def evaluate_record(
    *,
    record: dict,
    planner: TurnPlanner,
    chain: Any,
    gate: TurnProtocolGate,
    flows: Any,
    intents: dict,
    semaphore: asyncio.Semaphore,
) -> dict:
    async with semaphore:
        state = build_state_from_input(record["input"])
        prompt_payload = planner._build_input_prompt(state, flows, intents)
        raw_text = ""
        parsed_output = None
        parse_error = None
        protocol_gate_accepted = False
        gated_plan_dict = None
        try:
            raw_text = await chain.ainvoke(prompt_payload)
            parsed_output, parse_error = parse_json_text(raw_text)
            if parsed_output is not None:
                predicted_plan = TurnPlan.from_dict(parsed_output)
                gated = gate.process(
                    state,
                    turn_plan=predicted_plan,
                    flows=flows,
                    intents=intents,
                )
                protocol_gate_accepted = gated.accepted
                if gated.turn_plan is not None:
                    gated_plan_dict = turnplan_to_dict(gated.turn_plan)
        except Exception as exc:  # noqa: BLE001
            parse_error = f"{type(exc).__name__}: {exc}"

        gold_output = record["output"]
        predicted_output = parsed_output or {
            "task": None,
            "knowledge": None,
            "chitchat": None,
            "directive": None,
        }

        gold_track = active_track(gold_output)
        pred_track = active_track(predicted_output)
        all_null_as_expected_clarify_fallback = (
            gold_track == "all_null"
            and pred_track == "all_null"
            and not protocol_gate_accepted
        )

        gold_commands = extract_command_names(gold_output)
        pred_commands = extract_command_names(predicted_output)
        gold_flows = extract_flow_sequence(gold_output)
        pred_flows = extract_flow_sequence(predicted_output)
        gold_slots = extract_merged_slots(gold_output)
        pred_slots = extract_merged_slots(predicted_output)
        focused_object = record["input"].get("focused_object") or {}

        return {
            "id": record["id"],
            "bucket": record["bucket"],
            "gold_output": gold_output,
            "predicted_output": predicted_output,
            "gold_track": gold_track,
            "pred_track": pred_track,
            "track_match": gold_track == pred_track,
            "json_valid": parsed_output is not None,
            "protocol_gate_accepted": protocol_gate_accepted,
            "all_null_as_expected_clarify_fallback": all_null_as_expected_clarify_fallback,
            "effective_gate_pass": protocol_gate_accepted or all_null_as_expected_clarify_fallback,
            "gated_plan_dict": gated_plan_dict,
            "knowledge_match": gold_output["knowledge"] == predicted_output.get("knowledge"),
            "directive_match": gold_output["directive"] == predicted_output.get("directive"),
            "command_family_match": gold_commands == pred_commands,
            "flow_match": gold_flows == pred_flows,
            "slot_match": gold_slots == pred_slots,
            "gold_primary_flow": gold_flows[0] if gold_flows else None,
            "gated_primary_flow": extract_primary_flow(gated_plan_dict),
            "predicted_primary_flow": pred_flows[0] if pred_flows else None,
            "focused_object_type": focused_object.get("type"),
            "focused_object_id": focused_object.get("id"),
            "parse_error": parse_error,
            "raw_text": raw_text,
        }


def extract_primary_flow(output_payload: dict | None) -> str | None:
    if not output_payload:
        return None
    flows = extract_flow_sequence(output_payload)
    return flows[0] if flows else None


def compute_high_loss_read_only_metrics(predictions: list[dict]) -> dict[str, Any]:
    readonly_items = [
        item
        for item in predictions
        if item["gold_primary_flow"] in HIGH_LOSS_READ_ONLY_FLOW_IDS
    ]
    if not readonly_items:
        return {
            "count": 0,
            "system_success_rate": 0.0,
            "list_query_success_rate": 0.0,
            "work_order_runtime_success_rate": 0.0,
            "service_item_detail_success_rate": 0.0,
        }

    def business_success(item: dict) -> bool:
        plan_dict = item["gated_plan_dict"] or item["predicted_output"]
        predicted_flow = extract_primary_flow(plan_dict)
        merged_slots = extract_merged_slots(plan_dict)
        gold_flow = item["gold_primary_flow"]

        if gold_flow == "resident_work_orders_list_query":
            return predicted_flow == "resident_work_orders_list_query"
        if gold_flow == "resident_service_items_list_query":
            return predicted_flow == "resident_service_items_list_query"
        if gold_flow == "service_item_detail_query":
            return (
                predicted_flow == "service_item_detail_query"
                and bool(merged_slots.get("service_item_id") or item["focused_object_id"])
            )
        if gold_flow in WORK_ORDER_RUNTIME_FLOW_IDS:
            return (
                predicted_flow in WORK_ORDER_RUNTIME_FLOW_IDS
                and bool(merged_slots.get("work_order_id") or item["focused_object_id"])
            )
        return False

    def rate(items: list[dict]) -> float:
        if not items:
            return 0.0
        return sum(1 for item in items if business_success(item)) / len(items)

    list_items = [
        item
        for item in readonly_items
        if item["gold_primary_flow"] in {"resident_work_orders_list_query", "resident_service_items_list_query"}
    ]
    work_order_items = [
        item
        for item in readonly_items
        if item["gold_primary_flow"] in WORK_ORDER_RUNTIME_FLOW_IDS
    ]
    service_item_items = [
        item for item in readonly_items if item["gold_primary_flow"] == "service_item_detail_query"
    ]

    return {
        "count": len(readonly_items),
        "system_success_rate": rate(readonly_items),
        "list_query_success_rate": rate(list_items),
        "work_order_runtime_success_rate": rate(work_order_items),
        "service_item_detail_success_rate": rate(service_item_items),
    }


def compute_metrics(predictions: list[dict]) -> dict[str, Any]:
    total = len(predictions)
    by_bucket: dict[str, list[dict]] = defaultdict(list)
    for item in predictions:
        by_bucket[item["bucket"]].append(item)

    def subset(items: list[dict], predicate) -> list[dict]:
        return [item for item in items if predicate(item)]

    def rate(items: list[dict], key: str) -> float:
        if not items:
            return 0.0
        return sum(1 for item in items if item[key]) / len(items)

    gold_directive = subset(predictions, lambda item: item["gold_track"] == "directive")
    gold_all_null = subset(predictions, lambda item: item["gold_track"] == "all_null")
    gold_knowledge = subset(predictions, lambda item: item["gold_track"] == "knowledge")
    gold_task = subset(predictions, lambda item: item["gold_track"] == "task")
    gold_task_with_flow = subset(predictions, lambda item: item["gold_track"] == "task" and item["gold_output"]["task"] and any(cmd["command"] in {"start_flow", "resume_flow"} for cmd in item["gold_output"]["task"]["commands"]))
    gold_task_with_slots = subset(predictions, lambda item: item["gold_track"] == "task" and bool(extract_merged_slots(item["gold_output"])))
    all_null_clarify_fallback = subset(predictions, lambda item: item["all_null_as_expected_clarify_fallback"])
    effective_failures = subset(
        predictions,
        lambda item: (not item["track_match"]) or (not item["json_valid"]) or (not item["effective_gate_pass"]),
    )

    metrics = {
        "total_records": total,
        "all_null_clarify_fallback_count": len(all_null_clarify_fallback),
        "effective_failure_records": len(effective_failures),
        "top_level_track_accuracy": rate(predictions, "track_match"),
        "directive_accuracy": rate(gold_directive, "directive_match"),
        "all_null_accuracy": rate(gold_all_null, "track_match"),
        "knowledge_intent_accuracy": rate(gold_knowledge, "knowledge_match"),
        "task_command_family_accuracy": rate(gold_task, "command_family_match"),
        "flow_selection_accuracy": rate(gold_task_with_flow, "flow_match"),
        "slot_fill_exact_match": rate(gold_task_with_slots, "slot_match"),
        "json_valid_rate": rate(predictions, "json_valid"),
        "protocol_gate_pass_rate": rate(predictions, "protocol_gate_accepted"),
        "adjusted_protocol_gate_pass_rate": rate(predictions, "effective_gate_pass"),
        "knowledge_false_positive_rate": (
            sum(1 for item in gold_task if item["pred_track"] == "knowledge") / len(gold_task)
            if gold_task
            else 0.0
        ),
        "high_loss_read_only_metrics": compute_high_loss_read_only_metrics(predictions),
        "bucket_metrics": {bucket: build_bucket_metrics(items) for bucket, items in sorted(by_bucket.items())},
    }
    return metrics


def build_summary_markdown(label: str, metrics: dict[str, Any], predictions: list[dict]) -> str:
    lines = [
        f"# TurnPlan Runtime Eval - {label}",
        "",
        f"- total: {metrics['total_records']}",
        f"- all_null_clarify_fallback_count: {metrics['all_null_clarify_fallback_count']}",
        f"- effective_failure_records: {metrics['effective_failure_records']}",
        f"- top_level_track_accuracy: {metrics['top_level_track_accuracy']:.4f}",
        f"- directive_accuracy: {metrics['directive_accuracy']:.4f}",
        f"- all_null_accuracy: {metrics['all_null_accuracy']:.4f}",
        f"- knowledge_intent_accuracy: {metrics['knowledge_intent_accuracy']:.4f}",
        f"- task_command_family_accuracy: {metrics['task_command_family_accuracy']:.4f}",
        f"- flow_selection_accuracy: {metrics['flow_selection_accuracy']:.4f}",
        f"- slot_fill_exact_match: {metrics['slot_fill_exact_match']:.4f}",
        f"- knowledge_false_positive_rate: {metrics['knowledge_false_positive_rate']:.4f}",
        f"- json_valid_rate: {metrics['json_valid_rate']:.4f}",
        f"- protocol_gate_pass_rate: {metrics['protocol_gate_pass_rate']:.4f}",
        f"- adjusted_protocol_gate_pass_rate: {metrics['adjusted_protocol_gate_pass_rate']:.4f}",
        "",
        "## High-Loss Read-Only",
        "",
        f"- count: {metrics['high_loss_read_only_metrics']['count']}",
        f"- system_success_rate: {metrics['high_loss_read_only_metrics']['system_success_rate']:.4f}",
        f"- list_query_success_rate: {metrics['high_loss_read_only_metrics']['list_query_success_rate']:.4f}",
        f"- work_order_runtime_success_rate: {metrics['high_loss_read_only_metrics']['work_order_runtime_success_rate']:.4f}",
        f"- service_item_detail_success_rate: {metrics['high_loss_read_only_metrics']['service_item_detail_success_rate']:.4f}",
        "",
        "## Buckets",
        "",
        "| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for bucket, item in metrics["bucket_metrics"].items():
        lines.append(
            f"| {bucket} | {item['count']} | {item['track_accuracy']:.4f} | {item['json_valid_rate']:.4f} | {item['protocol_gate_pass_rate']:.4f} | {item['effective_protocol_gate_pass_rate']:.4f} |"
        )

    failures = [item for item in predictions if not item["track_match"] or not item["json_valid"] or not item["effective_gate_pass"]]
    lines.extend(["", "## Sample Failures", ""])
    for item in failures[:12]:
        lines.append(f"### {item['id']} ({item['bucket']})")
        lines.append(f"- gold_track: {item['gold_track']}")
        lines.append(f"- pred_track: {item['pred_track']}")
        lines.append(f"- json_valid: {item['json_valid']}")
        lines.append(f"- protocol_gate_accepted: {item['protocol_gate_accepted']}")
        lines.append(f"- effective_gate_pass: {item['effective_gate_pass']}")
        if item["parse_error"]:
            lines.append(f"- parse_error: `{item['parse_error']}`")
        lines.append("")
    return "\n".join(lines)


async def main() -> None:
    args = parse_args()
    records = load_records(args.canonical_dir / f"records_{args.split}.jsonl")
    if args.limit > 0:
        records = records[: args.limit]

    flows, intents = load_flows_and_intents()
    planner = TurnPlanner()
    gate = TurnProtocolGate(turn_validator=TurnPlanValidator())

    prompt_template = PromptTemplate.from_template(load_prompt("turn_plan"), template_format="jinja2")
    chain = prompt_template | llm | StrOutputParser()

    semaphore = asyncio.Semaphore(max(1, args.concurrency))
    predictions = await asyncio.gather(
        *[
            evaluate_record(
                record=record,
                planner=planner,
                chain=chain,
                gate=gate,
                flows=flows,
                intents=intents,
                semaphore=semaphore,
            )
            for record in records
        ]
    )

    metrics = compute_metrics(predictions)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with (args.output_dir / "predictions.jsonl").open("w", encoding="utf-8") as handle:
        for item in predictions:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")

    (args.output_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "summary.md").write_text(build_summary_markdown(args.label, metrics, predictions), encoding="utf-8")

    print(json.dumps({"label": args.label, "output_dir": str(args.output_dir), **metrics}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
