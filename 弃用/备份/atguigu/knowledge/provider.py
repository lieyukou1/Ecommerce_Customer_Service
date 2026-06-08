from dataclasses import dataclass, field
from typing import Any

from atguigu.domain.messages import FocusedObject
from atguigu.domain.state import DialogueState


PROPERTY_RULES: dict[str, str] = {
    "property_fee_rule": (
        "物业费类问题通常需要结合小区公示标准、房屋面积、收费周期和当前账单确认。"
        "如果用户要查具体金额、欠费或缴费方式，应继续引导到实际账单或收费页面核实。"
    ),
    "renovation_filing_rule": (
        "装修报备通常需要先确认装修时间、施工内容、施工人员信息，以及小区要求的材料。"
        "如果用户要办理报备，应继续收集时间、房号、联系人和施工范围等信息。"
    ),
    "parking_rule": (
        "停车规则通常关注车位类型、月租或临停收费、可停放时段，以及是否需要提前登记车牌。"
        "如果用户要处理具体停车业务，应继续确认车辆、车位和时段。"
    ),
    "pet_rule": (
        "宠物管理通常关注登记要求、牵引规则、公共区域行为约束，以及扰民和卫生责任。"
        "如果用户想确认能否饲养或需要办理什么手续，应继续让用户说明宠物类型和具体场景。"
    ),
    "community_rule": (
        "小区通用规则通常包括公共区域使用、噪音控制、门禁通行、装修时间和文明养宠等内容。"
        "若用户问的是某项具体制度，回答时应提醒以小区最新公告或物业通知为准。"
    ),
    "general_property_info": (
        "通用物业咨询通常需要先判断用户问的是收费、报修、投诉、停车、装修还是社区管理。"
        "如果范围太宽，应先帮用户收窄主题，再给出更具体的信息。"
    ),
}


@dataclass(slots=True)
class KnowledgeChunk:
    provider_id: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 1.0


@dataclass(slots=True)
class KnowledgeRequest:
    intent_id: str
    intent_description: str
    state: DialogueState | None = None


class KnowledgeProvider:
    provider_id: str

    def provide(self, request: KnowledgeRequest) -> list[KnowledgeChunk]:
        raise NotImplementedError


class FocusedObjectKnowledgeProvider(KnowledgeProvider):

    def __init__(self, provider_id: str, object_type: str, object_label: str):
        self.provider_id = provider_id
        self.object_type = object_type
        self.object_label = object_label

    def provide(self, request: KnowledgeRequest) -> list[KnowledgeChunk]:
        focused_object = request.state.focused_object if request.state is not None else None
        if focused_object is None or focused_object.type != self.object_type:
            return []

        content = self._build_content(focused_object, request.state)
        return [
            KnowledgeChunk(
                provider_id=self.provider_id,
                title=f"{self.object_label}当前上下文",
                content=content,
                metadata={
                    "object_type": focused_object.type,
                    "object_id": focused_object.id,
                },
            )
        ]

    def _build_content(self, focused_object: FocusedObject, state: DialogueState | None) -> str:
        lines = [f"{self.object_label}ID：{focused_object.id}"]

        if focused_object.title:
            lines.append(f"{self.object_label}标题：{focused_object.title}")

        for key, value in focused_object.attributes.items():
            if value is None or value == "":
                continue
            lines.append(f"{key}：{value}")

        if state is not None:
            lines.append(f"当前住户ID：{state.resident_id}")

        return "\n".join(lines)


class StaticRuleKnowledgeProvider(KnowledgeProvider):

    def __init__(self, provider_id: str, rules: dict[str, str], title_prefix: str):
        self.provider_id = provider_id
        self.rules = rules
        self.title_prefix = title_prefix

    def provide(self, request: KnowledgeRequest) -> list[KnowledgeChunk]:
        content = self.rules.get(request.intent_id)
        if not content:
            return []

        return [
            KnowledgeChunk(
                provider_id=self.provider_id,
                title=f"{self.title_prefix}{request.intent_description}",
                content=content,
                metadata={"intent_id": request.intent_id},
            )
        ]
