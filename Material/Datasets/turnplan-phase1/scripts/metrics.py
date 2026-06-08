from __future__ import annotations

import json
from collections import Counter, defaultdict

from dataset_contract import ALLOWED_FLOW_IDS, ALLOWED_KNOWLEDGE_INTENTS


def active_track(output_payload: dict) -> str:
    active = [name for name, value in output_payload.items() if value is not None]
    if not active:
        return "all_null"
    if len(active) > 1:
        return "multiple"
    return active[0]


def record_signature(record: dict) -> str:
    return json.dumps({"input": record["input"], "output": record["output"]}, ensure_ascii=False, sort_keys=True)


def compute_metrics(records: list[dict], system_prompt: str | None = None) -> dict:
    flow_counter = Counter()
    intent_counter = Counter()
    bucket_counter = Counter()
    track_counter = Counter()
    history_signatures = Counter()
    history_lengths = Counter()
    conversation_states = Counter()
    duplicate_counter = Counter()
    user_message_counter = Counter()
    object_ids = Counter()
    with_active_task = 0
    with_active_system_task = 0
    with_paused_tasks = 0
    multi_slot_set_slots = 0
    contact_phone_slot_records = 0
    complaint_confirm_negative_records = 0
    sft_ready_records = 0
    language_naturalness_pass_records = 0
    history_state_consistency_pass_records = 0
    object_slot_consistency_pass_records = 0
    state_alignment_pass_records = 0
    object_alignment_pass_records = 0
    slot_alignment_pass_records = 0

    for record in records:
        bucket_counter[record["bucket"]] += 1
        track = active_track(record["output"])
        track_counter[track] += 1
        duplicate_counter[record_signature(record)] += 1
        user_message_counter[record["input"]["user_message"]] += 1
        history_signatures[json.dumps(record["input"]["history"], ensure_ascii=False, sort_keys=True)] += 1
        history_lengths[len(record["input"]["history"])] += 1
        conversation_states[record["input"]["runtime_state"]["conversation_state"]] += 1

        focused_object = record["input"]["focused_object"]
        if focused_object is not None:
            object_ids[focused_object["id"]] += 1

        if record["input"]["active_task"] is not None:
            with_active_task += 1
        if record["input"]["active_system_task"] is not None:
            with_active_system_task += 1
        if record["input"]["paused_tasks"]:
            with_paused_tasks += 1

        audit_meta = record.get("audit_meta") or {}
        if audit_meta.get("passed_for_sft") is True:
            sft_ready_records += 1
        if audit_meta.get("language_naturalness_checked") is True:
            language_naturalness_pass_records += 1
        if audit_meta.get("timeline_consistency_checked") is True:
            history_state_consistency_pass_records += 1
        if (
            audit_meta.get("object_alignment_checked") is True
            and audit_meta.get("slot_alignment_checked") is True
        ):
            object_slot_consistency_pass_records += 1
        if audit_meta.get("state_alignment_checked") is True:
            state_alignment_pass_records += 1
        if audit_meta.get("object_alignment_checked") is True:
            object_alignment_pass_records += 1
        if audit_meta.get("slot_alignment_checked") is True:
            slot_alignment_pass_records += 1

        task_payload = record["output"]["task"]
        if task_payload is not None:
            for command in task_payload.get("commands", []):
                if command["command"] in {"start_flow", "resume_flow"} and command.get("flow"):
                    flow_counter[command["flow"]] += 1
                if command["command"] == "set_slots":
                    slots = command.get("slots", {})
                    if len(slots) > 1:
                        multi_slot_set_slots += 1
                    if "contact_phone" in slots:
                        contact_phone_slot_records += 1
                if (
                    command["command"] == "cancel_flow"
                    and record["input"]["active_task"] is not None
                    and record["input"]["active_task"].get("step_id") == "collect_complaint_confirm"
                ):
                    complaint_confirm_negative_records += 1

        knowledge_payload = record["output"]["knowledge"]
        if knowledge_payload is not None:
            for intent in knowledge_payload.get("intents", []):
                intent_counter[intent] += 1

    exact_duplicate_pairs = sum(count - 1 for count in duplicate_counter.values() if count > 1)
    repeated_user_messages = sum(count - 1 for count in user_message_counter.values() if count > 1)
    total_records = len(records)

    contract_flags = {
        "mentions_intents_array": system_prompt is not None and '"intents": ["intent_id"]' in system_prompt,
        "mentions_flow_field": system_prompt is not None and "flow 标识字段名必须是 flow" in system_prompt,
        "mentions_active_system_task": system_prompt is not None and "active_system_task.flow_id == \"system_collect_information\"" in system_prompt,
    }

    return {
        "total_records": total_records,
        "unique_pairs": len(duplicate_counter),
        "duplicate_pairs": exact_duplicate_pairs,
        "duplicate_ratio": exact_duplicate_pairs / total_records if total_records else 0.0,
        "bucket_counts": dict(bucket_counter),
        "track_counts": dict(track_counter),
        "flow_counts": {flow_id: flow_counter.get(flow_id, 0) for flow_id in ALLOWED_FLOW_IDS},
        "knowledge_intent_counts": {intent: intent_counter.get(intent, 0) for intent in ALLOWED_KNOWLEDGE_INTENTS},
        "unique_histories": len(history_signatures),
        "history_length_distribution": dict(history_lengths),
        "conversation_state_distribution": dict(conversation_states),
        "unique_user_messages": len(user_message_counter),
        "repeated_user_messages": repeated_user_messages,
        "unique_object_ids": len(object_ids),
        "active_task_records": with_active_task,
        "active_system_task_records": with_active_system_task,
        "paused_task_records": with_paused_tasks,
        "multi_slot_set_slots_records": multi_slot_set_slots,
        "contact_phone_slot_records": contact_phone_slot_records,
        "complaint_confirm_negative_records": complaint_confirm_negative_records,
        "sft_ready_records": sft_ready_records,
        "sft_ready_pass_rate": sft_ready_records / total_records if total_records else 0.0,
        "language_naturalness_pass_rate": (
            language_naturalness_pass_records / total_records if total_records else 0.0
        ),
        "history_state_consistency_pass_rate": (
            history_state_consistency_pass_records / total_records if total_records else 0.0
        ),
        "object_slot_consistency_pass_rate": (
            object_slot_consistency_pass_records / total_records if total_records else 0.0
        ),
        "state_alignment_pass_rate": (
            state_alignment_pass_records / total_records if total_records else 0.0
        ),
        "object_alignment_pass_rate": (
            object_alignment_pass_records / total_records if total_records else 0.0
        ),
        "slot_alignment_pass_rate": (
            slot_alignment_pass_records / total_records if total_records else 0.0
        ),
        "contract_flags": contract_flags,
    }
