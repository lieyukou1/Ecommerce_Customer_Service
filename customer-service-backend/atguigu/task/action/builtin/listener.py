from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class ActionListener(Action):
    """
    功能：作为 flow 推进的“停下等待用户”哨兵 action。
    """

    name = "action_listen"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        功能：返回一个空结果，表示当前 flow 应该把控制权交回用户输入。

        输入：
        - state: 当前运行时状态。
        - action_kwargs: 当前 action 参数；该 action 实际不消费参数。

        输出：
        - ActionResult: 空消息、空槽位更新结果。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 无。
        """
        return ActionResult()
