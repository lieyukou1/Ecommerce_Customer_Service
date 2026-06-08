from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.objects import (
    build_object_messages,
    build_service_item_object,
)


class AnswerResidentServiceItems(Action):
    name = "action_lookup_resident_service_items"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """

        :param state:
        :param action_kwargs:
        :return:
        """
        data = await request_property_api("GET", f"/residents/{state.resident_id}/service-items")
        service_items = (data or {}).get("service_items") or []
        objects = [build_service_item_object(item) for item in service_items[:5] if isinstance(item, dict)]
        messages = build_object_messages(
            objects,
            empty_text="当前住户下暂时没有查到可展示的服务项目。",
        )
        return ActionResult(messages=messages)
