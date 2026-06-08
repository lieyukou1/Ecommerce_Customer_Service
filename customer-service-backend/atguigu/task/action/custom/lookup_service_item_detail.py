from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_service_item_id


class LookupServiceItemDetail(Action):
    """
    功能：查询服务项目详情，并把结果回写到项目详情槽位。
    """

    name = "action_lookup_service_item_detail"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：读取服务项目 ID，查询详情接口，并输出项目详情类槽位更新。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: 当前 action 参数；该 action 实际不依赖额外参数。

        输出：
        - ActionResult: 不直接回消息，只通过 `slot_updates` 提供项目详情。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 会请求中台接口；通过 `slot_updates` 回写项目详情信息。
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
