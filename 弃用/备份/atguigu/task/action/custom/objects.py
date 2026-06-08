from __future__ import annotations

from atguigu.domain.messages import BotMessage, FocusedObject

from atguigu.task.action.custom.formatting import stringify_value


def build_work_order_object(data: dict[str, object]) -> FocusedObject:
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
    if not objects:
        return [BotMessage(text=empty_text)]
    return [BotMessage(object=item) for item in objects]
