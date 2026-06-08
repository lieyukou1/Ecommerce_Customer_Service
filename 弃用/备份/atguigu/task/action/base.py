from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field
from atguigu.domain.state import DialogueState
from atguigu.domain.messages import BotMessage

"""
内置
action_response:(ActionResult:messages:"请先选择一个商品，再继续咨询")
action_listen: (ActionResult())
自定义：
action_recommend_similar_products
action_lookup_order_status(ActionResult:(slot_updates:{第三返回的}))
action_lookup_logistics (ActionResult:(slot_updates:{第三返回的}))
"""


@dataclass
class ActionResult:
    messages: list[BotMessage] = field(default_factory=list)

    slot_updates: dict[str, Any] = field(default_factory=dict)


class Action(ABC):
    name:str

    @abstractmethod
    async def run(self,
                  state: DialogueState,
                  action_kwargs: dict[str, Any], ) -> ActionResult:
        pass
