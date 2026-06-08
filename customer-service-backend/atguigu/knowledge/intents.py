from dataclasses import dataclass, field


@dataclass(slots=True)
class KnowledgeIntent:
    id: str
    description: str
    provider_ids: list[str] = field(default_factory=list)
    requires_object: str | None = None


KNOWLEDGE_INTENTS: dict[str, KnowledgeIntent] = {
    "service_item_info": KnowledgeIntent(
        id="service_item_info",
        description="咨询某个服务项目的说明、费用、办理方式或可预约情况",
        provider_ids=["api.service_item"],
        requires_object="service_item",
    ),
    "work_order_info": KnowledgeIntent(
        id="work_order_info",
        description="咨询某条工单的状态、进度、处理信息或上下文说明",
        provider_ids=["api.work_order"],
        requires_object="work_order",
    ),
    "property_fee_rule": KnowledgeIntent(
        id="property_fee_rule",
        description="咨询物业费相关规则、缴费说明或账单范围",
        provider_ids=["faq.default", "rag.default"],
    ),
    "renovation_filing_rule": KnowledgeIntent(
        id="renovation_filing_rule",
        description="咨询装修报备规则、材料要求或办理前置条件",
        provider_ids=["faq.default", "rag.default"],
    ),
    "parking_rule": KnowledgeIntent(
        id="parking_rule",
        description="咨询停车管理规则、收费方式或登记要求",
        provider_ids=["faq.default", "rag.default"],
    ),
    "pet_rule": KnowledgeIntent(
        id="pet_rule",
        description="咨询宠物管理规则、登记要求或公共区域约束",
        provider_ids=["faq.default", "rag.default"],
    ),
    "community_rule": KnowledgeIntent(
        id="community_rule",
        description="咨询小区通用管理规则、公共区域规范或行为要求",
        provider_ids=["faq.default", "rag.default"],
    ),
    "general_property_info": KnowledgeIntent(
        id="general_property_info",
        description="一般性物业信息咨询，需要继续收窄到具体主题",
        provider_ids=["faq.default", "rag.default"],
    ),
}
