from typing import Any

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.custom.resident_rules import build_rule_answer, normalize_rule_topic
from atguigu.task.action.custom.slots import get_slot


class AnswerResidentRule(Action):
    """
    功能：根据当前规则主题槽位返回住户规则答复。
    """

    name = "action_answer_resident_rule"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：读取 `rule_topic` 槽位，生成规则回复并回写归一化主题。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: 当前 action 参数；该 action 实际不依赖额外参数。

        输出：
        - ActionResult: 包含规则答复消息，以及可选的 `rule_topic` 归一化更新。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 不直接改状态；通过 `slot_updates` 回写归一化后的 `rule_topic`。
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
