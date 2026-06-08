from __future__ import annotations

from copy import deepcopy
from typing import Any


ANSWER_LIKE_OBJECT_KEYS = {
    "status",
    "amount",
    "price",
    "service_status",
    "summary",
    "description",
}


def sanitize_record_input(input_payload: dict[str, Any]) -> dict[str, Any]:
    """Shrink canonical input into the planner-focused training schema."""
    payload = deepcopy(input_payload)
    return {
        "history": _sanitize_history(payload.get("history", [])),
        "runtime_state": _sanitize_runtime_state(payload.get("runtime_state")),
        "active_task": _sanitize_task_context(payload.get("active_task")),
        "active_system_task": _sanitize_system_task(payload.get("active_system_task")),
        "paused_tasks": _sanitize_paused_tasks(payload.get("paused_tasks", [])),
        "focused_object": _sanitize_focused_object(payload.get("focused_object")),
        "user_message": payload.get("user_message", ""),
    }


def _sanitize_history(history: list[dict[str, Any]]) -> list[dict[str, str]]:
    sanitized: list[dict[str, str]] = []
    for item in history[-4:]:
        sanitized.append(
            {
                "role": item.get("role", ""),
                "text": item.get("text", ""),
            }
        )
    return sanitized


def _sanitize_runtime_state(runtime_state: dict[str, Any] | None) -> dict[str, Any]:
    runtime_state = runtime_state or {}
    return {
        "conversation_state": runtime_state.get("conversation_state"),
        "last_route": _sanitize_last_route(runtime_state.get("last_route")),
        "last_task_outcome": _sanitize_last_task_outcome(runtime_state.get("last_task_outcome")),
    }


def _sanitize_last_route(last_route: dict[str, Any] | None) -> dict[str, Any] | None:
    if not last_route:
        return None
    if "semantic_kind" not in last_route and "event" not in last_route and "kind" not in last_route:
        return None
    payload: dict[str, Any] = {}
    if last_route.get("semantic_kind") is not None:
        payload["semantic_kind"] = last_route.get("semantic_kind")
    if last_route.get("event") is not None:
        payload["event"] = last_route.get("event")
    if last_route.get("kind") is not None:
        payload["kind"] = last_route.get("kind")
    return payload or None


def _sanitize_last_task_outcome(last_task_outcome: dict[str, Any] | None) -> dict[str, Any] | None:
    if not last_task_outcome:
        return None
    payload: dict[str, Any] = {}
    if last_task_outcome.get("semantic_kind") is not None:
        payload["semantic_kind"] = last_task_outcome.get("semantic_kind")
    if last_task_outcome.get("flow_id") is not None:
        payload["flow_id"] = last_task_outcome.get("flow_id")
    if last_task_outcome.get("kind") is not None:
        payload["kind"] = last_task_outcome.get("kind")
    return payload or None


def _sanitize_task_context(task_context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not task_context:
        return None
    filled_slots = dict(task_context.get("filled_slots") or task_context.get("slots") or {})
    missing_slots = list(task_context.get("missing_slots") or [])
    return {
        "flow_id": task_context.get("flow_id"),
        "step_id": task_context.get("step_id"),
        "missing_slots": missing_slots,
        "filled_slots": filled_slots,
    }


def _sanitize_system_task(system_task: dict[str, Any] | None) -> dict[str, Any] | None:
    if not system_task:
        return None
    slot_name = system_task.get("slot_name")
    if slot_name is None:
        slot_name = (system_task.get("slots") or {}).get("target_slot")
    return {
        "flow_id": system_task.get("flow_id"),
        "step_id": system_task.get("step_id"),
        "slot_name": slot_name,
    }


def _sanitize_paused_tasks(paused_tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    for item in paused_tasks:
        sanitized_item = _sanitize_task_context(item)
        if sanitized_item is None:
            continue
        sanitized.append(
            {
                "flow_id": sanitized_item.get("flow_id"),
                "step_id": sanitized_item.get("step_id"),
            }
        )
    return sanitized


def _sanitize_focused_object(focused_object: dict[str, Any] | None) -> dict[str, Any] | None:
    if not focused_object:
        return None
    attributes = dict(focused_object.get("attributes") or {})
    route_attributes = {
        key: value
        for key, value in attributes.items()
        if key not in ANSWER_LIKE_OBJECT_KEYS
    }
    payload = {
        "type": focused_object.get("type"),
        "id": focused_object.get("id"),
        "title": focused_object.get("title", ""),
    }
    if route_attributes:
        payload["attributes"] = route_attributes
    return payload
