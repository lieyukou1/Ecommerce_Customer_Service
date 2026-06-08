from __future__ import annotations

from atguigu.domain.messages import BotMessage, FocusedObject
from atguigu.task.action.custom.formatting import stringify_value


def build_work_order_object(data: dict[str, object]) -> FocusedObject:
    """
    功能：把中台工单数据转换成前后端统一使用的 FocusedObject。

    输入：
    - data: 中台返回的单条工单字典。

    输出：
    - FocusedObject: 标准化后的工单对象。

    调用情况：
    - `AnswerResidentWorkOrders.run()`

    副作用：
    - 无。
    """
    work_order_id = stringify_value(data.get("work_order_id"))
    title = stringify_value(data.get("title"), work_order_id)
    attributes = {
        "status": stringify_value(data.get("status")),
        "summary": stringify_value(data.get("summary") or data.get("status_desc")),
        "amount": stringify_value(data.get("amount")),
        "appointment_time": stringify_value(data.get("appointment_time")),
        "category": stringify_value(data.get("category")),
        "cover_url": stringify_value(data.get("cover_url")),
    }
    return FocusedObject(
        id=work_order_id,
        type="work_order",
        title=title,
        attributes=attributes,
    )


def build_service_item_object(data: dict[str, object]) -> FocusedObject:
    """
    功能：把中台服务项目数据转换成统一的 FocusedObject。

    输入：
    - data: 中台返回的单条服务项目字典。

    输出：
    - FocusedObject: 标准化后的服务项目对象。

    调用情况：
    - `AnswerResidentServiceItems.run()`

    副作用：
    - 无。
    """
    service_item_id = stringify_value(data.get("service_item_id"))
    title = stringify_value(data.get("title"), service_item_id)
    attributes = {
        "service_status": stringify_value(data.get("service_status")),
        "description": stringify_value(data.get("description")),
        "price": stringify_value(data.get("price")),
        "cover_url": stringify_value(data.get("cover_url")),
    }
    return FocusedObject(
        id=service_item_id,
        type="service_item",
        title=title,
        attributes=attributes,
    )


def build_object_messages(
    objects: list[FocusedObject],
    *,
    empty_text: str,
) -> list[BotMessage]:
    """
    功能：把对象列表转换成发送给前端的对象消息列表。

    输入：
    - objects: 待展示的对象列表。
    - empty_text: 对象为空时返回的提示文案。

    输出：
    - list[BotMessage]: 非空时返回对象消息；为空时返回单条文本消息。

    调用情况：
    - 多个“列表查询类” action 复用。

    副作用：
    - 无。
    """
    if not objects:
        return [BotMessage(text=empty_text)]
    return [BotMessage(object=item) for item in objects]
