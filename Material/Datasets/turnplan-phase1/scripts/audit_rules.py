from __future__ import annotations

from typing import Any


SYSTEM_TERMS = (
    "track",
    "flow",
    "slot",
    "set_slots",
    "start_flow",
    "resume_flow",
    "cancel_flow",
    "directive",
    "knowledge",
    "all-null",
)
SELF_LABEL_TERMS = (
    "我是",
    "我是在补",
    "这是投诉原因",
    "这是催办原因",
    "原因补充",
    "我现在是在",
)
DEICTIC_OBJECT_TERMS = ("这单", "这个工单", "这个项目", "这个服务", "这件事", "这个")


def build_audit_meta(record: dict[str, Any]) -> dict[str, Any]:
    notes: list[str] = []
    natural = check_language_naturalness(record, notes)
    timeline = check_timeline_consistency(record, notes)
    state_alignment = check_state_alignment(record, notes)
    object_alignment = check_object_alignment(record, notes)
    slot_alignment = check_slot_alignment(record, notes)
    return {
        "language_naturalness_checked": natural,
        "timeline_consistency_checked": timeline,
        "state_alignment_checked": state_alignment,
        "object_alignment_checked": object_alignment,
        "slot_alignment_checked": slot_alignment,
        "passed_for_sft": all([natural, timeline, state_alignment, object_alignment, slot_alignment]),
        "audit_notes": notes,
    }


def build_semantic_meta(record: dict[str, Any]) -> dict[str, Any]:
    bucket = record["bucket"]
    semantic_family = _semantic_family_from_record(record)
    state_dependency = _state_dependency_from_record(record)
    return {
        "semantic_family": semantic_family,
        "state_dependency": state_dependency,
        "read_only_resolution_target": _read_only_resolution_target(record),
        "contrast_group": record.get("semantic_meta", {}).get("contrast_group"),
        "decision_basis": _decision_basis(record),
    }


def check_language_naturalness(record: dict[str, Any], notes: list[str]) -> bool:
    texts = [record["input"].get("user_message", "")]
    texts.extend(item.get("text", "") for item in record["input"].get("history", []) if item.get("role") == "user")
    for text in texts:
        if any(term in text for term in SELF_LABEL_TERMS):
            notes.append("language: explicit self-labeling remains in user text")
            return False
        if "比如" in text:
            notes.append("language: template residue '比如' remains in user text")
            return False
        if any(term in text for term in SYSTEM_TERMS):
            notes.append("language: user text still contains system-internal terminology")
            return False
    return True


def check_timeline_consistency(record: dict[str, Any], notes: list[str]) -> bool:
    history = record["input"].get("history", [])
    runtime = record["input"].get("runtime_state", {})
    conversation_state = (runtime.get("conversation_state") or "").upper()
    active_task = record["input"].get("active_task")
    paused_tasks = record["input"].get("paused_tasks") or []
    if conversation_state == "ACTIVE_TASK" and active_task is None:
        notes.append("timeline: ACTIVE_TASK without active_task context")
        return False
    if conversation_state == "TRANSITIONING" and not paused_tasks:
        notes.append("timeline: TRANSITIONING without paused_tasks context")
        return False
    if active_task is not None and not history:
        notes.append("timeline: active task exists but history has no lead-in context")
        return False
    return True


def check_state_alignment(record: dict[str, Any], notes: list[str]) -> bool:
    bucket = record["bucket"]
    output = record["output"]
    active_task = record["input"].get("active_task")
    active_system_task = record["input"].get("active_system_task")
    task_payload = output.get("task")
    if bucket == "active_task_slot_fill" and active_task is None and active_system_task is None:
        notes.append("state: active_task_slot_fill missing active runtime context")
        return False
    if bucket in {"active_task_slot_fill", "task_interrupt_resume_cancel"} and task_payload is None:
        notes.append("state: task-centric bucket lost task output")
        return False
    if output.get("directive") is not None and active_task is None and not record["input"].get("focused_object"):
        notes.append("state: exit_runtime has no runtime context to exit")
        return False
    return True


def check_object_alignment(record: dict[str, Any], notes: list[str]) -> bool:
    focused_object = record["input"].get("focused_object")
    user_message = record["input"].get("user_message", "")
    if focused_object is None:
        return True
    if focused_object.get("type") == "service_item" and ("工单" in user_message or "这单" in user_message):
        notes.append("object: user refers to work order while focused_object is service_item")
        return False
    if focused_object.get("type") == "work_order" and "服务项目" in user_message:
        notes.append("object: user refers to service item while focused_object is work_order")
        return False
    return True


def check_slot_alignment(record: dict[str, Any], notes: list[str]) -> bool:
    task_payload = record["output"].get("task")
    if task_payload is None:
        return True
    focused_object = record["input"].get("focused_object") or {}
    object_id = focused_object.get("id")
    for command in task_payload.get("commands", []):
        if command.get("command") != "set_slots":
            continue
        slots = command.get("slots", {})
        if "work_order_id" in slots and object_id and slots["work_order_id"] != object_id:
            notes.append("slot: work_order_id does not match focused_object.id")
            return False
        if "service_item_id" in slots and object_id and slots["service_item_id"] != object_id:
            notes.append("slot: service_item_id does not match focused_object.id")
            return False
    return True


def _semantic_family_from_record(record: dict[str, Any]) -> str:
    bucket = record["bucket"]
    if bucket == "directive_exit_runtime":
        return "exit_runtime"
    if bucket == "chitchat":
        return "social"
    if bucket == "ambiguous_all_null":
        return "need_clarify"
    if bucket == "active_task_slot_fill":
        return "continue_current_task"
    if bucket == "task_interrupt_resume_cancel":
        return "interrupt_resume_cancel"
    if bucket in {"work_order_business_urge", "work_order_business_complaint"}:
        return "start_or_switch_business_task"
    if bucket == "work_order_read_only_task":
        return "read_only_request"
    if bucket in {"service_item_knowledge", "object_context_followup"}:
        return "read_only_request"
    return bucket


def _state_dependency_from_record(record: dict[str, Any]) -> str:
    if record["input"].get("active_task") is not None:
        return "active_task_required"
    if record["input"].get("active_system_task") is not None:
        return "active_system_task_required"
    if record["input"].get("focused_object") is not None:
        return "focused_object_required"
    return "standalone"


def _read_only_resolution_target(record: dict[str, Any]) -> str | None:
    task_payload = record["output"].get("task")
    knowledge_payload = record["output"].get("knowledge")
    if task_payload:
        return "runtime_flow"
    if knowledge_payload:
        return "knowledge"
    return None


def _decision_basis(record: dict[str, Any]) -> list[str]:
    basis: list[str] = []
    if record["input"].get("active_task") is not None:
        basis.append("active_task")
    if record["input"].get("active_system_task") is not None:
        basis.append("active_system_task")
    if record["input"].get("focused_object") is not None:
        basis.append("focused_object")
    if record["input"].get("paused_tasks"):
        basis.append("paused_tasks")
    if not basis:
        basis.append("user_message")
    return basis
