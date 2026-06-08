from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState


@dataclass
class ActionResult:
    """
    功能：承载单个 action 的执行结果。
    """

    messages: list[BotMessage] = field(default_factory=list)
    slot_updates: dict[str, Any] = field(default_factory=dict)


class Action(ABC):
    """
    功能：定义 flow action 的统一执行接口。
    """

    name: str

    @abstractmethod
    async def run(
        self,
        state: DialogueState,
        action_kwargs: dict[str, Any],
    ) -> ActionResult:
        """
        功能：执行一个 flow action，并返回消息与槽位更新。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: YAML action step 传入的参数字典。

        输出：
        - ActionResult: action 产生的消息和槽位更新。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 具体副作用由子类决定；推荐通过 `slot_updates` 间接回写状态。
        """
        raise NotImplementedError
