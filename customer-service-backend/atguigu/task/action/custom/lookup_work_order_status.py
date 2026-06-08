from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_work_order_id


class LookupWorkOrderStatus(Action):
    """
    功能：查询工单状态，并把结果写回工单状态相关槽位。
    """

    name = "action_lookup_work_order_status"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：读取当前工单 ID，查询状态接口，并输出状态类槽位更新。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: 当前 action 参数；该 action 实际不依赖额外参数。

        输出：
        - ActionResult: 不直接回消息，只通过 `slot_updates` 提供状态结果。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 会请求中台接口；通过 `slot_updates` 回写工单状态信息。
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
