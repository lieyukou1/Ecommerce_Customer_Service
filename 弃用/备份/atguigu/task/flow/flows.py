from dataclasses import dataclass, field
from typing import List, Dict

from atguigu.task.flow.steps import FlowStep, StartedFlowStep


@dataclass(slots=True)
class FlowSlot:
    name: str
    type: str = 'any'
    label: str = ''
    description: str = ''


@dataclass(slots=True)
class Flow:
    id: str
    name: str | None = None
    description: str = ''
    steps: List[FlowStep] = field(default_factory=list)
    slots: List[FlowSlot] = field(default_factory=list)

    def start_step(self) -> StartedFlowStep | None:
        """
        返回流程的开始步骤
        """
        for step in self.steps:
            if isinstance(step, StartedFlowStep):
                return step
        return None

    def get_step_by_id(self, step_id: str) -> FlowStep | None:
        """
        根据id查找
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
        for flow in self.flows:
            if flow.id == flow_id:
                return flow
        return None
