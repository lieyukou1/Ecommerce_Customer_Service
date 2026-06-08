from atguigu.knowledge.provider import (
    PROPERTY_RULES,
    FocusedObjectKnowledgeProvider,
    KnowledgeProvider,
    StaticRuleKnowledgeProvider,
)


class KnowledgeProviderRegistry:

    def __init__(self, providers: dict[str, KnowledgeProvider] | None = None):
        self.providers = providers or {}

    def register(self, provider: KnowledgeProvider) -> None:
        self.providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> KnowledgeProvider | None:
        return self.providers.get(provider_id)


def build_default_registry() -> KnowledgeProviderRegistry:
    registry = KnowledgeProviderRegistry()
    registry.register(
        FocusedObjectKnowledgeProvider(
            provider_id="api.service_item",
            object_type="service_item",
            object_label="服务项目",
        )
    )
    registry.register(
        FocusedObjectKnowledgeProvider(
            provider_id="api.work_order",
            object_type="work_order",
            object_label="工单",
        )
    )
    registry.register(
        StaticRuleKnowledgeProvider(
            provider_id="faq.default",
            rules=PROPERTY_RULES,
            title_prefix="规则知识：",
        )
    )
    registry.register(
        StaticRuleKnowledgeProvider(
            provider_id="rag.default",
            rules=PROPERTY_RULES,
            title_prefix="补充说明：",
        )
    )
    return registry
