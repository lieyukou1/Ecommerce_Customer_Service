from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_work_order_id


class LookupWorkOrderProgress(Action):
    name = "action_lookup_work_order_progress"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """

        :param state:
        :param action_kwargs:
        :return:
        """
        work_order_id = get_work_order_id(state)
        data = None
        if work_order_id:
            data = await request_property_api("GET", f"/work-orders/{work_order_id}/progress")

        traces = (data or {}).get("traces") or []
        trace_summary = "；".join(
            f"{stringify_value(item.get('time'))} {stringify_value(item.get('desc'))}".strip()
            for item in traces[:3]
            if isinstance(item, dict)
        )

        slot_updates = {
            "work_order_id": work_order_id,
            "current_stage": stringify_value((data or {}).get("current_stage"), "暂未查到"),
            "stage_desc": stringify_value((data or {}).get("stage_desc"), "暂时没有查询到处理进度说明。"),
            "service_team": stringify_value((data or {}).get("service_team"), "待分配"),
            "assignee_name": stringify_value((data or {}).get("assignee_name"), "待分配"),
            "assignee_phone_masked": stringify_value((data or {}).get("assignee_phone_masked")),
            "progress_trace_summary": trace_summary,
        }

        return ActionResult(slot_updates=slot_updates)
