from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_slot, get_work_order_id


class SubmitComplaintRequest(Action):
    name = "action_submit_complaint_request"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """

        :param state:
        :param action_kwargs:
        :return:
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
