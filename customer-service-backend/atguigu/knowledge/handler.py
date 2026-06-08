from typing import Dict

from atguigu.domain.messages import BotMessage, UserMessage
from atguigu.domain.state import DialogueState, Turn
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.knowledge.provider import KnowledgeChunk, KnowledgeRequest
from atguigu.knowledge.registry import KnowledgeProviderRegistry, build_default_registry
from atguigu.knowledge.responder import KnowledgeResponder
from atguigu.plan.turn_plan import KnowledgeTurnPlan
from atguigu.prompt.history_builder import HistoryBuilder


class KnowledgeHandler:
    """
    功能：承接 knowledge 轨请求，负责“解析意图 -> 聚合知识片段 -> 组织回复”。
    """

    def __init__(
        self,
        knowledge_intents: Dict[str, KnowledgeIntent],
        registry: KnowledgeProviderRegistry | None = None,
        responder: KnowledgeResponder | None = None,
    ):
        """
        功能：构造知识轨处理器。

        输入：
        - knowledge_intents: 当前系统支持的知识意图注册表。
        - registry: 可选的知识提供者注册表；为空时使用默认注册表。
        - responder: 可选的知识回复器；为空时使用默认回复器。

        输出：
        - 无返回值；初始化知识轨依赖。

        调用情况：
        - 装配层创建，供文本轨的 knowledge 分支调用。

        副作用：
        - 无。
        """
        self.knowledge_intents = knowledge_intents
        self.registry = registry or build_default_registry()
        self.responder = responder or KnowledgeResponder()

    def handle(
        self,
        state: DialogueState | None = None,
        turn_plan: KnowledgeTurnPlan | None = None,
        user_message: UserMessage | None = None,
        recent_turns: list[Turn] | None = None,
    ) -> list[BotMessage]:
        """
        功能：处理 knowledge 轨请求，收集知识片段并生成最终回复。

        输入：
        - state: 当前运行时状态，可为空。
        - turn_plan: 当前 knowledge 计划，可为空。
        - user_message: 显式传入的用户消息；为空时尝试从 state.pending_turn 推断。
        - recent_turns: 显式传入的最近历史；为空时尝试从当前会话读取。

        输出：
        - list[BotMessage]: 知识轨生成的机器人消息列表。

        调用情况：
        - `TextTurnHandler._execute_context()` 的 knowledge 分支。

        副作用：
        - 无状态写入；只调用 provider 和 responder。
        """
        resolved_message = user_message
        if resolved_message is None and state is not None and state.pending_turn is not None:
            resolved_message = state.pending_turn.user_message

        if recent_turns is None and state is not None and state.current_session() is not None:
            recent_turns = state.current_session().turns[-10:]

        if turn_plan is None or not turn_plan.intents:
            return [BotMessage(text="你想咨询哪方面的物业信息？比如工单、服务项目，或者收费、装修、停车这类规则。")]

        rendered_message = (
            HistoryBuilder._render_user_message(resolved_message)
            if resolved_message is not None
            else None
        )
        history = HistoryBuilder.build(recent_turns or [])

        # 只保留当前注册表中真实存在的意图，避免无效 intent 继续向下游扩散。
        resolved_intents = [
            self.knowledge_intents[intent_id]
            for intent_id in turn_plan.intents
            if intent_id in self.knowledge_intents
        ]
        if not resolved_intents:
            return [BotMessage(text="这次我还没识别出你具体想咨询的知识点。你可以换个更具体的说法再试一次。")]

        # 某些知识意图依赖 focused object；对象没就位时，先直接回提示。
        missing_object_reply = self._build_missing_object_reply(state, resolved_intents)
        if missing_object_reply is not None:
            return [BotMessage(text=missing_object_reply)]

        chunks = self._collect_knowledge_chunks(state, resolved_intents)
        return self.responder.respond(
            user_message=rendered_message,
            history=history,
            knowledge_chunks=chunks,
            intent_descriptions=[intent.description for intent in resolved_intents],
        )

    def _collect_knowledge_chunks(
        self,
        state: DialogueState | None,
        intents: list[KnowledgeIntent],
    ) -> list[KnowledgeChunk]:
        """
        功能：从各 provider 聚合知识片段，并做去重。

        输入：
        - state: 当前运行时状态，可为空。
        - intents: 已解析出的知识意图列表。

        输出：
        - list[KnowledgeChunk]: 去重后的知识片段列表。

        调用情况：
        - `handle()`

        副作用：
        - 无；只查询 provider。
        """
        chunks: list[KnowledgeChunk] = []
        seen: set[tuple[str, str, str]] = set()

        for intent in intents:
            request = KnowledgeRequest(
                intent_id=intent.id,
                intent_description=intent.description,
                state=state,
            )

            # 一个 intent 可以同时依赖多个 provider，这里把它们依次拼起来。
            for provider_id in intent.provider_ids:
                provider = self.registry.get(provider_id)
                if provider is None:
                    continue

                for chunk in provider.provide(request):
                    signature = (chunk.provider_id, chunk.title, chunk.content)
                    if signature in seen:
                        continue
                    seen.add(signature)
                    chunks.append(chunk)

        return chunks

    def _build_missing_object_reply(
        self,
        state: DialogueState | None,
        intents: list[KnowledgeIntent],
    ) -> str | None:
        """
        功能：为依赖 focused object 的知识意图生成缺对象提示。

        输入：
        - state: 当前运行时状态，可为空。
        - intents: 已解析出的知识意图列表。

        输出：
        - str | None: 缺对象时返回提示话术，否则返回 None。

        调用情况：
        - `handle()`

        副作用：
        - 无。
        """
        focused_object = state.focused_object if state is not None else None

        for intent in intents:
            if intent.requires_object is None:
                continue
            if focused_object is not None and focused_object.type == intent.requires_object:
                continue

            if intent.requires_object == "work_order":
                return "这类问题需要先明确是哪条工单。你可以先选中一条工单，我再继续帮你看。"
            if intent.requires_object == "service_item":
                return "这类问题需要先明确是哪个服务项目。你可以先选中一个服务项目，我再继续帮你看。"

        return None
