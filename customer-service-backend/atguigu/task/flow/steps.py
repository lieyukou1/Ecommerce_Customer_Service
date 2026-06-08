from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from atguigu.task.flow.links import ConditionalLink, FallbackLink, FlowStepLink, StaticLink


class FlowStepType(Enum):
    """
    功能：标记 flow step 的四种基础类型。
    """

    START = "start"
    ACTION = "action"
    END = "end"
    COLLECT = "collect"


@dataclass(slots=True)
class ResponseDefinition:
    """
    功能：描述 collect step 或验证失败时要返回给用户的响应内容。
    """

    text: str
    mode: str = "static"
    prompt: str | None = None


@dataclass(slots=True)
class SlotValidation:
    condition: str
    failure_response: ResponseDefinition | None = None


def _build_links(link_data: str | list[Dict[str, Any]]) -> List[FlowStepLink]:
    """
    功能：把 YAML 中的 `next` 配置加载成 step link 列表。

    输入：
    - link_data: 字符串形式的静态跳转，或列表形式的条件/兜底跳转定义。

    输出：
    - List[FlowStepLink]: 结构化后的 step 边列表。

    调用情况：
    - 由 `FlowStep.base_load_field()` 调用。

    副作用：
    - 无。
    """
    if isinstance(link_data, str):
        return [StaticLink(link_data)]

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
    功能：所有 flow step 的基础模型。
    """

    id: str
    type: FlowStepType
    next: List[FlowStepLink] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "FlowStep":
        """
        功能：根据 step 类型把 YAML 字典分发到具体 step 子类。

        输入：
        - step_data: 当前 step 的原始 YAML 字典。

        输出：
        - FlowStep: 对应子类的 step 对象。

        调用情况：
        - 由 `FlowLoader._load_flows()` 调用。

        副作用：
        - 无。
        """
        step_type = step_data["type"]
        clz = TYPE_TO_FLOW_STEP[step_type]
        return clz.from_dict(step_data)

    @staticmethod
    def base_load_field(base_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        功能：提取所有 step 公共字段。

        输入：
        - base_data: 当前 step 的原始 YAML 字典。

        输出：
        - Dict[str, Any]: 子类构造时需要复用的公共字段字典。

        调用情况：
        - 由各 step 子类的 `from_dict()` 调用。

        副作用：
        - 无。
        """
        return {
            "id": base_data["id"],
            "type": FlowStepType(base_data["type"]),
            "description": base_data.get("description", ""),
            "next": _build_links(base_data["next"]),
        }


@dataclass(slots=True)
class StartedFlowStep(FlowStep):
    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "StartedFlowStep":
        """
        功能：反序列化 start step。

        输入：
        - step_data: 当前 step 的原始 YAML 字典。

        输出：
        - StartedFlowStep: 反序列化后的 start step。

        调用情况：
        - 由 `FlowStep.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(**FlowStep.base_load_field(step_data))


@dataclass(slots=True)
class ActionFlowStep(FlowStep):
    action: str = ""
    args: Dict[str, Any] | str = field(default_factory=dict)

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "ActionFlowStep":
        """
        功能：反序列化 action step。

        输入：
        - step_data: 当前 step 的原始 YAML 字典。

        输出：
        - ActionFlowStep: 反序列化后的 action step。

        调用情况：
        - 由 `FlowStep.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(
            **FlowStep.base_load_field(step_data),
            action=step_data["action"],
            args=step_data.get("args", {}),
        )


@dataclass(slots=True)
class EndFlowStep(FlowStep):
    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "EndFlowStep":
        """
        功能：反序列化 end step。

        输入：
        - step_data: 当前 step 的原始 YAML 字典。

        输出：
        - EndFlowStep: 反序列化后的 end step。

        调用情况：
        - 由 `FlowStep.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(**FlowStep.base_load_field(step_data))


@dataclass(slots=True, kw_only=True)
class CollectedFlowStep(FlowStep):
    slot_name: str = ""
    response: ResponseDefinition
    validate: SlotValidation | None = None

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "CollectedFlowStep":
        """
        功能：反序列化 collect step，包括槽位提示和可选验证规则。

        输入：
        - step_data: 当前 step 的原始 YAML 字典。

        输出：
        - CollectedFlowStep: 反序列化后的 collect step。

        调用情况：
        - 由 `FlowStep.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(
            **FlowStep.base_load_field(step_data),
            slot_name=step_data["slot_name"],
            response=ResponseDefinition(
                text=step_data["response"]["text"],
                mode=step_data["response"].get("mode", "static"),
                prompt=step_data["response"].get("prompt"),
            ),
            validate=SlotValidation(
                condition=step_data["validate"]["condition"],
                failure_response=ResponseDefinition(
                    text=step_data["validate"]["failure_response"]["text"],
                    mode=step_data["validate"]["failure_response"].get("mode", "static"),
                    prompt=step_data["validate"]["failure_response"].get("prompt"),
                ) if step_data["validate"].get("failure_response") else None,
            ) if step_data.get("validate") else None,
        )


TYPE_TO_FLOW_STEP: Dict[str, type[FlowStep]] = {
    "start": StartedFlowStep,
    "action": ActionFlowStep,
    "end": EndFlowStep,
    "collect": CollectedFlowStep,
}
