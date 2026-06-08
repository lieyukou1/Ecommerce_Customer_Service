from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.objects import (
    build_object_messages,
    build_work_order_object,
)


class AnswerResidentWorkOrders(Action):
    name = "action_lookup_resident_work_orders"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """

        :param state:
        :param action_kwargs:
        :return:
        """
        data = await request_property_api("GET", f"/residents/{state.resident_id}/work-orders")
        work_orders = (data or {}).get("work_orders") or []
        objects = [build_work_order_object(item) for item in work_orders[:5] if isinstance(item, dict)]
        messages = build_object_messages(
            objects,
            empty_text="当前住户下暂时没有查到可展示的工单。",
        )
        return ActionResult(messages=messages)
