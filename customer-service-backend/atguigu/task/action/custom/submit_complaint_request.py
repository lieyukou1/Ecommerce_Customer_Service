from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_slot, get_work_order_id


class SubmitComplaintRequest(Action):
    """
    功能：提交工单投诉请求，并把提交结果写回槽位。
    """

    name = "action_submit_complaint_request"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：读取当前工单和投诉原因，提交投诉请求，并返回提交结果槽位。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: 当前 action 参数；该 action 实际不依赖额外参数。

        输出：
        - ActionResult: 不直接回消息，只通过 `slot_updates` 提供投诉提交结果。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 会请求中台接口；通过 `slot_updates` 回写投诉请求信息。
        """
        work_order_id = get_work_order_id(state)
        complaint_reason = stringify_value(get_slot(state, "complaint_reason"), "对当前处理结果有异议")

        data = None
        if work_order_id:
            data = await request_property_api(
                "POST",
                f"/work-orders/{work_order_id}/complaint-requests",
                json_body={
                    "submitted_by": state.resident_id,
                    "reason": complaint_reason,
                },
            )

        if not work_order_id:
            slot_updates = {
                "work_order_id": "",
                "complaint_reason": complaint_reason,
                "complaint_request_id": "",
                "complaint_request_status": "missing_work_order_id",
                "complaint_request_status_desc": "缺少工单号，当前还没有真正提交投诉请求。",
            }
        else:
            slot_updates = {
                "work_order_id": work_order_id,
                "complaint_reason": complaint_reason,
                "complaint_request_id": stringify_value((data or {}).get("request_id")),
                "complaint_request_status": stringify_value((data or {}).get("status"), "submitted"),
                "complaint_request_status_desc": stringify_value(
                    (data or {}).get("status_desc"),
                    "投诉请求已记录，等待物业客服进一步处理。",
                ),
            }

        return ActionResult(slot_updates=slot_updates)
