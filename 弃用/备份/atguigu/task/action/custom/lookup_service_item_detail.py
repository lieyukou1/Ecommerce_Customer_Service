from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_service_item_id


class LookupServiceItemDetail(Action):
    name = "action_lookup_service_item_detail"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """

        :param state:
        :param action_kwargs:
        :return:
        """
        service_item_id = get_service_item_id(state)
        data = None
        if service_item_id:
            data = await request_property_api("GET", f"/service-items/{service_item_id}")

        slot_updates = {
            "service_item_id": service_item_id,
            "service_item_status": stringify_value((data or {}).get("service_status"), "暂未查到"),
            "service_item_price": stringify_value((data or {}).get("price"), "待确认"),
            "service_item_description": stringify_value((data or {}).get("description"), "暂时没有查询到服务项目说明。"),
        }

        return ActionResult(slot_updates=slot_updates)
