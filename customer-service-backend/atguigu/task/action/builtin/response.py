from dataclasses import asdict
from typing import Any

from jinja2 import Template

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class ActionResponse(Action):
    """
    功能：把模板化文本渲染成最终机器人回复。
    """

    name = "action_response"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：渲染 `action_response` 文本模板并返回消息。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: action step 传入的参数，通常包含 `text` 模板。

        输出：
        - ActionResult: 包含单条文本消息的结果。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 无状态写入；只读取 task / focused object 上下文做模板渲染。
        """
        text = action_kwargs.get("text") or ""
        current_task = state.current_active_task()
        active_slots = state.active_task.slots if state.active_task is not None else {}
        context = asdict(current_task) if current_task is not None else {}
        focused_object = state.focused_object.to_dict() if state.focused_object is not None else None

        rendered_text = Template(str(text)).render(
            slots=active_slots,
            context=context,
            resident_id=state.resident_id,
            focused_object=focused_object,
        )

        return ActionResult(messages=[BotMessage(text=rendered_text)])
