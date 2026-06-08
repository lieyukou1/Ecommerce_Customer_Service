from typing import Any

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.resident_rules import build_rule_answer, normalize_rule_topic
from atguigu.task.action.custom.slots import get_slot


class AnswerResidentRule(Action):
    name = "action_answer_resident_rule"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """

        :param state:
        :param action_kwargs:
        :return:
        """
        rule_topic = str(get_slot(state, "rule_topic", ""))
        normalized_topic = normalize_rule_topic(rule_topic)
        answer = build_rule_answer(rule_topic)

        slot_updates = {}
        if normalized_topic:
            slot_updates["rule_topic"] = normalized_topic

        return ActionResult(
            messages=[BotMessage(text=answer)],
            slot_updates=slot_updates,
        )
