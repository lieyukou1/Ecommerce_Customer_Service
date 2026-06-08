from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_slot, get_work_order_id


class SubmitWorkOrderUrgeRequest(Action):
    """
    功能：提交工单催办请求，并把提交结果写回槽位。
    """

    name = "action_submit_work_order_urge_request"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：读取当前工单和催办原因，提交催办请求，并返回提交结果槽位。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: 当前 action 参数；该 action 实际不依赖额外参数。

        输出：
        - ActionResult: 不直接回消息，只通过 `slot_updates` 提供提交结果。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 会请求中台接口；通过 `slot_updates` 回写催办请求信息。
        """
        work_order_id = get_work_order_id(state)
        urge_reason = stringify_value(get_slot(state, "urge_reason"), "希望尽快处理")

        data = None
        if work_order_id:
            data = await request_property_api(
                "POST",
                f"/work-orders/{work_order_id}/urge-requests",
                json_body={
                    "submitted_by": state.resident_id,
                    "reason": urge_reason,
                },
            )

        if not work_order_id:
            slot_updates = {
                "work_order_id": "",
                "urge_reason": urge_reason,
                "urge_request_id": "",
                "urge_request_status": "missing_work_order_id",
                "urge_request_status_desc": "缺少工单号，当前还没有真正提交催办请求。",
            }
        else:
            slot_updates = {
                "work_order_id": work_order_id,
                "urge_reason": urge_reason,
                "urge_request_id": stringify_value((data or {}).get("request_id")),
                "urge_request_status": stringify_value((data or {}).get("status"), "submitted"),
                "urge_request_status_desc": stringify_value(
                    (data or {}).get("status_desc"),
                    "催办请求已记录，等待物业侧进一步处理。",
                ),
            }

        return ActionResult(slot_updates=slot_updates)
