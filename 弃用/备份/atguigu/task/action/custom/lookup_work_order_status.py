from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_work_order_id


class LookupWorkOrderStatus(Action):
    name = "action_lookup_work_order_status"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """

        :param state:
        :param action_kwargs:
        :return:
        """
        work_order_id = get_work_order_id(state)
        data = None
        if work_order_id:
            data = await request_property_api("GET", f"/work-orders/{work_order_id}/status")

        slot_updates = {
            "work_order_id": work_order_id,
            "work_order_status": stringify_value((data or {}).get("status"), "暂未查到"),
            "work_order_status_desc": stringify_value((data or {}).get("status_desc"), "暂时没有查询到工单状态说明。"),
            "work_order_priority": stringify_value((data or {}).get("priority"), "未知"),
        }

        return ActionResult(slot_updates=slot_updates)
