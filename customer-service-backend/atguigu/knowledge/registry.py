from atguigu.knowledge.provider import (
    PROPERTY_RULES,
    FocusedObjectKnowledgeProvider,
    KnowledgeProvider,
    StaticRuleKnowledgeProvider,
)


class KnowledgeProviderRegistry:
    def __init__(self, providers: dict[str, KnowledgeProvider] | None = None):
        """
        功能：构造知识提供者注册表。

        输入：
        - providers: 可选的 provider 映射；为空时使用空注册表。

        输出：
        - 无返回值；初始化注册表内部字典。

        调用情况：
        - 由 `KnowledgeHandler` 和默认注册表构建函数调用。

        副作用：
        - 无。
        """
        self.providers = providers or {}

    def register(self, provider: KnowledgeProvider) -> None:
        """
        功能：向注册表中注册一个知识提供者。

        输入：
        - provider: 具体的知识提供者实例。

        输出：
        - 无返回值。

        调用情况：
        - 由 `build_default_registry()` 调用。

        副作用：
        - 会修改 `providers` 字典。
        """
        self.providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> KnowledgeProvider | None:
        """
        功能：按 provider_id 获取知识提供者。

        输入：
        - provider_id: 目标 provider 标识。

        输出：
        - KnowledgeProvider | None: 命中时返回 provider，否则返回 None。

        调用情况：
        - 由 `KnowledgeHandler._collect_knowledge_chunks()` 调用。

        副作用：
        - 无。
        """
        return self.providers.get(provider_id)


def build_default_registry() -> KnowledgeProviderRegistry:
    """
    功能：构造项目默认的知识提供者注册表。

    输入：
    - 无。

    输出：
    - KnowledgeProviderRegistry: 已注册工单、服务项目和静态规则 provider 的默认注册表。

    调用情况：
    - 由 `KnowledgeHandler.__init__()` 在未传自定义 registry 时调用。

    副作用：
    - 无外部副作用；会在新 registry 对象上注册多个 provider。
    """
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
