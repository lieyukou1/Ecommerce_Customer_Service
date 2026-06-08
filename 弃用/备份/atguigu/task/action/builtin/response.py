from dataclasses import asdict
from typing import Any

from jinja2 import Template

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.domain.messages import BotMessage


class ActionResponse(Action):
    name = "action_response"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        响应内容
        :param state:
        :param action_kwargs:
        :return:
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
