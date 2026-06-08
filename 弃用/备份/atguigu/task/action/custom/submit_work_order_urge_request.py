from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_slot, get_work_order_id


class SubmitWorkOrderUrgeRequest(Action):
    name = "action_submit_work_order_urge_request"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """

        :param state:
        :param action_kwargs:
        :return:
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
