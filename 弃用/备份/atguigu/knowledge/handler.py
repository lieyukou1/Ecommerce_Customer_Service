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

    def __init__(
        self,
        knowledge_intents: Dict[str, KnowledgeIntent],
        registry: KnowledgeProviderRegistry | None = None,
        responder: KnowledgeResponder | None = None,
    ):
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

        resolved_intents = [
            self.knowledge_intents[intent_id]
            for intent_id in turn_plan.intents
            if intent_id in self.knowledge_intents
        ]
        if not resolved_intents:
            return [BotMessage(text="这次我还没识别出你具体想咨询的知识点。你可以换个更具体的说法再试一次。")]

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
        chunks: list[KnowledgeChunk] = []
        seen: set[tuple[str, str, str]] = set()

        for intent in intents:
            request = KnowledgeRequest(
                intent_id=intent.id,
                intent_description=intent.description,
                state=state,
            )

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
