from __future__ import annotations

from typing import Any

from atguigu.domain.state import DialogueState


def get_active_slots(state: DialogueState) -> dict[str, Any]:
    """
    功能：读取当前 active_task 的全部槽位。

    输入：
    - state: 当前运行时状态。

    输出：
    - dict[str, Any]: 当前任务槽位；无 active_task 时返回空字典。

    调用情况：
    - 当前自定义 action 的槽位读取 helper 复用。

    副作用：
    - 无。
    """
    if state.active_task is None:
        return {}
    return state.active_task.slots


def get_slot(state: DialogueState, slot_name: str, default: Any = None) -> Any:
    """
    功能：读取当前任务中的单个槽位值。

    输入：
    - state: 当前运行时状态。
    - slot_name: 槽位名。
    - default: 槽位缺失时的默认值。

    输出：
    - Any: 当前槽位值或默认值。

    调用情况：
    - 多个自定义 action 复用。

    副作用：
    - 无。
    """
    return get_active_slots(state).get(slot_name, default)


def get_focused_object_attribute(
    state: DialogueState,
    *,
    object_type: str,
    attribute_name: str,
    default: Any = None,
) -> Any:
    """
    功能：按对象类型读取 focused object 上的属性值。

    输入：
    - state: 当前运行时状态。
    - object_type: 期望的对象类型。
    - attribute_name: 要读取的属性名。
    - default: 对象不匹配或属性不存在时的默认值。

    输出：
    - Any: 命中时返回属性值，否则返回默认值。

    调用情况：
    - 需要对象提示信息的 action 复用。

    副作用：
    - 无。
    """
    focused_object = state.focused_object
    if focused_object is None or focused_object.type != object_type:
        return default
    return focused_object.attributes.get(attribute_name, default)


def get_work_order_id(state: DialogueState) -> str:
    """
    功能：读取当前上下文里的工单 ID。

    输入：
    - state: 当前运行时状态。

    输出：
    - str: 优先返回 slot 中的工单 ID，其次回退到 focused object。

    调用情况：
    - 工单类自定义 action 复用。

    副作用：
    - 无。
    """
    slot_value = get_slot(state, "work_order_id")
    if slot_value:
        return str(slot_value)

    focused_object = state.focused_object
    if focused_object is not None and focused_object.type == "work_order":
        return focused_object.id

    return ""


def get_service_item_id(state: DialogueState) -> str:
    """
    功能：读取当前上下文里的服务项目 ID。

    输入：
    - state: 当前运行时状态。

    输出：
    - str: 优先返回 slot 中的服务项目 ID，其次回退到 focused object。

    调用情况：
    - 服务项目类自定义 action 复用。

    副作用：
    - 无。
    """
    slot_value = get_slot(state, "service_item_id")
    if slot_value:
        return str(slot_value)

    focused_object = state.focused_object
    if focused_object is not None and focused_object.type == "service_item":
        return focused_object.id

    return ""
