from __future__ import annotations

from typing import Any

from atguigu.domain.state import DialogueState


def get_active_slots(state: DialogueState) -> dict[str, Any]:
    if state.active_task is None:
        return {}
    return state.active_task.slots


def get_slot(state: DialogueState, slot_name: str, default: Any = None) -> Any:
    return get_active_slots(state).get(slot_name, default)


def get_focused_object_attribute(
    state: DialogueState,
    *,
    object_type: str,
    attribute_name: str,
    default: Any = None,
) -> Any:
    focused_object = state.focused_object
    if focused_object is None or focused_object.type != object_type:
        return default
    return focused_object.attributes.get(attribute_name, default)


def get_work_order_id(state: DialogueState) -> str:
    slot_value = get_slot(state, "work_order_id")
    if slot_value:
        return str(slot_value)

    focused_object = state.focused_object
    if focused_object is not None and focused_object.type == "work_order":
        return focused_object.id

    return ""


def get_service_item_id(state: DialogueState) -> str:
    slot_value = get_slot(state, "service_item_id")
    if slot_value:
        return str(slot_value)

    focused_object = state.focused_object
    if focused_object is not None and focused_object.type == "service_item":
        return focused_object.id

    return ""
