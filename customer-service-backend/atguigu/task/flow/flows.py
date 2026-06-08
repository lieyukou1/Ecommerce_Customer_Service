from dataclasses import dataclass, field
from typing import Dict, List

from atguigu.task.flow.steps import FlowStep, StartedFlowStep


@dataclass(slots=True)
class FlowSlot:
    name: str
    type: str = "any"
    label: str = ""
    description: str = ""


@dataclass(slots=True)
class Flow:
    id: str
    name: str | None = None
    description: str = ""
    steps: List[FlowStep] = field(default_factory=list)
    slots: List[FlowSlot] = field(default_factory=list)

    def start_step(self) -> StartedFlowStep | None:
        """
        功能：返回当前 flow 的起始 step。

        输入：
        - 无显式输入；依赖当前 flow 的 `steps` 列表。

        输出：
        - StartedFlowStep | None: 找到 start step 时返回对应对象，否则返回 None。

        调用情况：
        - 由 command processor、flow executor 等执行层逻辑调用。

        副作用：
        - 无。
        """
        for step in self.steps:
            if isinstance(step, StartedFlowStep):
                return step
        return None

    def get_step_by_id(self, step_id: str) -> FlowStep | None:
        """
        功能：按 step_id 从当前 flow 中查找 step。

        输入：
        - step_id: 目标 step 标识。

        输出：
        - FlowStep | None: 命中时返回 step，对应不到时返回 None。

        调用情况：
        - 由 flow executor 推进 flow 时调用。

        副作用：
        - 无。
        """
        for step in self.steps:
            if step.id == step_id:
                return step
        return None


@dataclass(slots=True)
class FlowList:
    flows: List[Flow] = field(default_factory=list)
    slots: Dict[str, FlowSlot] = field(default_factory=dict)

    def get_flow_by_id(self, flow_id: str) -> Flow | None:
        """
        功能：按 flow_id 查找 flow。

        输入：
        - flow_id: 目标 flow 标识。

        输出：
        - Flow | None: 命中时返回 flow，对应不到时返回 None。

        调用情况：
        - 由 command processor、flow executor、validator 等多处调用。

        副作用：
        - 无。
        """
        for flow in self.flows:
            if flow.id == flow_id:
                return flow
        return None
