from dataclasses import dataclass, field
from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import ActionResult
from atguigu.task.action.registry import ActionRegistry


@dataclass
class ActionCall:
    """
    功能：描述一次 action 执行请求。
    """

    action_name: str
    action_kwargs: dict[str, Any] = field(default_factory=dict)


class ActionRunner:
    """
    功能：根据 action name 从注册表分发并执行 action。
    """

    def __init__(self, registry: ActionRegistry):
        """
        功能：构造 action 执行器。

        输入：
        - registry: 已注册的 action 注册表。

        输出：
        - 无返回值；保存依赖。

        调用情况：
        - `build_action_runner()`

        副作用：
        - 无。
        """
        self.registry = registry

    async def run(self, action_call: ActionCall, state: DialogueState) -> ActionResult:
        """
        功能：执行一次 action call。

        输入：
        - action_call: 当前动作调用请求。
        - state: 当前运行时状态。

        输出：
        - ActionResult: action 执行结果。

        调用情况：
        - `FlowExecutor.run_task()`

        副作用：
        - 具体副作用取决于 action 实现本身。
        """
        action_name = action_call.action_name
        action = self.registry.get(action_name)
        return await action.run(state=state, action_kwargs=action_call.action_kwargs)
