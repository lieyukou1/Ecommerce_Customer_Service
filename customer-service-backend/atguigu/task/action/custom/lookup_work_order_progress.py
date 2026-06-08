from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.formatting import stringify_value
from atguigu.task.action.custom.slots import get_work_order_id


class LookupWorkOrderProgress(Action):
    """
    功能：查询工单处理进度，并整理成进度类槽位。
    """

    name = "action_lookup_work_order_progress"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：读取工单 ID，查询进度接口，并把结果压缩成 flow 后续可渲染的槽位。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: 当前 action 参数；该 action 实际不依赖额外参数。

        输出：
        - ActionResult: 不直接回消息，只返回进度相关 `slot_updates`。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 会请求中台接口；通过 `slot_updates` 回写进度信息。
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
