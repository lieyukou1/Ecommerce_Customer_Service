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
    """知识回复阶段的最小上下文片段。"""

    provider_id: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    score: float = 1.0


@dataclass(slots=True)
class KnowledgeRequest:
    """传给 provider 的查询请求。"""

    intent_id: str
    intent_description: str
    state: DialogueState | None = None


class KnowledgeProvider:
    """知识片段提供者抽象基类。"""

    provider_id: str

    def provide(self, request: KnowledgeRequest) -> list[KnowledgeChunk]:
        """
        功能：根据知识请求提供知识片段。

        输入：
        - request: 当前知识查询请求。

        输出：
        - list[KnowledgeChunk]: 当前 provider 返回的知识片段列表。

        调用情况：
        - `KnowledgeHandler._collect_knowledge_chunks()`

        副作用：
        - 无；子类中可读取状态或静态规则。
        """
        raise NotImplementedError


class FocusedObjectKnowledgeProvider(KnowledgeProvider):
    """
    功能：把当前 focused object 压缩成知识问答可用的上下文片段。
    """

    def __init__(self, provider_id: str, object_type: str, object_label: str):
        """
        功能：构造基于 focused object 输出上下文知识的 provider。

        输入：
        - provider_id: provider 标识。
        - object_type: 适用的对象类型，如 `work_order` 或 `service_item`。
        - object_label: 对外展示时使用的对象标签。

        输出：
        - 无返回值；初始化 provider 元信息。

        调用情况：
        - `build_default_registry()`

        副作用：
        - 无。
        """
        self.provider_id = provider_id
        self.object_type = object_type
        self.object_label = object_label

    def provide(self, request: KnowledgeRequest) -> list[KnowledgeChunk]:
        """
        功能：把当前 focused object 转成一条 API 上下文知识片段。

        输入：
        - request: 当前知识查询请求。

        输出：
        - list[KnowledgeChunk]: 命中目标对象类型时返回一条 chunk，否则返回空列表。

        调用情况：
        - `KnowledgeHandler._collect_knowledge_chunks()`

        副作用：
        - 无；只读 `request.state`。
        """
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
        """
        功能：把 focused object 及部分状态信息压缩成结构化文本。

        输入：
        - focused_object: 当前聚焦对象。
        - state: 当前运行时状态，可为空。

        输出：
        - str: 多行 `字段：值` 形式的上下文文本。

        调用情况：
        - `provide()`

        副作用：
        - 无。
        """
        lines = [f"{self.object_label}ID：{focused_object.id}"]
        if focused_object.title:
            lines.append(f"{self.object_label}标题：{focused_object.title}")

        # 对象 attributes 直接透传给知识回复层，便于回答价格、状态、描述这类追问。
        for key, value in focused_object.attributes.items():
            if value is None or value == "":
                continue
            lines.append(f"{key}：{value}")

        if state is not None:
            lines.append(f"当前住户ID：{state.resident_id}")

        return "\n".join(lines)


class StaticRuleKnowledgeProvider(KnowledgeProvider):
    """
    功能：从静态规则库中返回知识片段。
    """

    def __init__(self, provider_id: str, rules: dict[str, str], title_prefix: str):
        """
        功能：构造基于静态规则文本输出知识片段的 provider。

        输入：
        - provider_id: provider 标识。
        - rules: 意图 ID 到规则文本的映射。
        - title_prefix: chunk 标题前缀。

        输出：
        - 无返回值；初始化静态规则 provider。

        调用情况：
        - `build_default_registry()`

        副作用：
        - 无。
        """
        self.provider_id = provider_id
        self.rules = rules
        self.title_prefix = title_prefix

    def provide(self, request: KnowledgeRequest) -> list[KnowledgeChunk]:
        """
        功能：按 intent_id 返回对应静态规则知识。

        输入：
        - request: 当前知识查询请求。

        输出：
        - list[KnowledgeChunk]: 命中规则时返回一条 chunk，否则返回空列表。

        调用情况：
        - `KnowledgeHandler._collect_knowledge_chunks()`

        副作用：
        - 无。
        """
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
