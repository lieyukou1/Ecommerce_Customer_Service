from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any

from atguigu.task.flow.links import FlowStepLink, ConditionalLink, FallbackLink, StaticLink


class FlowStepType(Enum):
    """
    流程的步骤类型
    流程概念（管理节点的容器）
    步骤概念（节点）
    """
    START = "start"
    ACTION = "action"
    END = "end"
    COLLECT = "collect"


@dataclass(slots=True)
class ResponseDefinition:
    """
    响应的模式:静态模式(static) 改写模式(rephrase) | prompt
    响应内容(静态内容 改写后的内容)
    “”:一段输出而已 不需要定义逻辑（渲染）
    None:未定义/缺失字段：定义逻辑 处理
    """
    text: str
    mode: str = "static"
    prompt: str | None = None


@dataclass(slots=True)
class SlotValidation:
    """

    """
    condition: str
    failure_response: ResponseDefinition | None = None


def _build_links(link_data: str | list[Dict[str, Any]]) -> List[FlowStepLink]:
    """

    """
    # 1.字符串
    if isinstance(link_data, str):
        return [StaticLink(link_data)]
    # 2.列表
    else:
        links = []
        for link in link_data:
            if "if" in link:
                links.append(ConditionalLink(condition=link["if"], target=link["then"]))
            else:
                links.append(FallbackLink(link["else"]))
        return links


@dataclass(slots=True)
class FlowStep:
    """
    业务流程、系统）流程步骤 模版
    """
    id: str
    type: FlowStepType
    next: List[FlowStepLink] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "FlowStep":
        """
        从yaml中读取到字典模型
        """
        step_type = step_data["type"]
        clz = TYPE_TO_FLOW_STEP[step_type]
        return clz.from_dict(step_data)

    @staticmethod
    def base_load_field(base_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        加载各个步骤的基础字段
        """
        return {
            "id": base_data["id"],
            "type": FlowStepType(base_data["type"]),
            "description": base_data.get("description", ""),
            "next": _build_links(base_data['next'])
        }


@dataclass(slots=True)
class StartedFlowStep(FlowStep):

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "StartedFlowStep":
        return cls(**FlowStep.base_load_field(step_data))


@dataclass(slots=True)
class ActionFlowStep(FlowStep):
    action: str = ""
    args: Dict[str, Any] | str = field(default_factory=dict)

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "ActionFlowStep":
        return cls(
            **FlowStep.base_load_field(step_data),
            action=step_data['action'],
            args=step_data.get('args', {})
        )


@dataclass(slots=True)
class EndFlowStep(FlowStep):

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "EndFlowStep":
        return cls(**FlowStep.base_load_field(step_data))


@dataclass(slots=True, kw_only=True)
class CollectedFlowStep(FlowStep):
    slot_name: str = ""
    response: ResponseDefinition
    validate: SlotValidation | None = None

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "CollectedFlowStep":
        return cls(
            **FlowStep.base_load_field(step_data),
            slot_name=step_data['slot_name'],
            response=ResponseDefinition(
                text=step_data['response']['text'],
                mode=step_data['response'].get('mode', 'static'),
                prompt=step_data['response'].get('prompt')
            ),
            validate=SlotValidation(
                condition=step_data['validate']['condition'],
                failure_response=ResponseDefinition(
                    text=step_data['validate']['failure_response']['text'],
                    mode=step_data['validate']['failure_response'].get('mode', 'static'),
                    prompt=step_data['validate']['failure_response'].get('prompt')
                ) if step_data['validate'].get('failure_response') else None
            ) if step_data.get('validate') else None
        )


TYPE_TO_FLOW_STEP: Dict[str, type[FlowStep]] = {
    "start": StartedFlowStep,
    "action": ActionFlowStep,
    "end": EndFlowStep,
    "collect": CollectedFlowStep
}
