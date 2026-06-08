from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.objects import build_object_messages, build_service_item_object


class AnswerResidentServiceItems(Action):
    """
    功能：查询当前住户可展示的服务项目列表，并返回对象消息。
    """

    name = "action_lookup_resident_service_items"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：调用中台获取住户服务项目，并把结果压缩成前端可选对象列表。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: 当前 action 参数；该 action 实际不依赖额外参数。

        输出：
        - ActionResult: 包含服务项目对象消息列表；没有数据时返回兜底文本。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 会请求中台接口；不直接改状态。
        """
        data = await request_property_api("GET", f"/residents/{state.resident_id}/service-items")
        service_items = (data or {}).get("service_items") or []
        objects = [build_service_item_object(item) for item in service_items[:5] if isinstance(item, dict)]
        messages = build_object_messages(
            objects,
            empty_text="当前住户下暂时没有查到可展示的服务项目。",
        )
        return ActionResult(messages=messages)
