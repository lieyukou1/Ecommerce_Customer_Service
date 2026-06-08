import re
import time
from typing import Dict

from atguigu.chitchat.handler import ChitchatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.domain.messages import BotMessage, MessageType, ProcessResult, UserMessage
from atguigu.domain.state import DialogueState
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.turn_plan import ClarifyReason
from atguigu.plan.turn_validator import TurnPlanValidator
from atguigu.task.command.models import Command, SetSlotsCommand
from atguigu.task.flow.flows import FlowList
from atguigu.task.flow.steps import CollectedFlowStep
from atguigu.task.handler import TaskHandler


class DialogueEngine:
    EXIT_RUNTIME_TEXTS = {
        "取消",
        "退出",
        "结束",
        "返回",
        "重置",
        "重来",
        "重新开始",
        "清空状态",
        "清空上下文",
        "退出当前",
        "取消当前",
        "结束当前",
        "不看这个了",
        "不聊这个了",
        "先不看了",
        "先不用了",
        "算了",
    }
    EXIT_RUNTIME_PHRASES = {
        "取消吧",
        "不用了",
        "不需要了",
        "不继续了",
        "不聊了",
        "不问了",
        "不看了",
        "不弄了",
        "不办了",
        "先这样吧",
        "先这样",
        "就这样吧",
        "就这样",
        "到这里吧",
        "先到这里吧",
        "先退出吧",
        "先取消吧",
        "先不看了",
        "先不问了",
        "先不办了",
        "先不弄了",
        "重新来吧",
    }

    def __init__(
        self,
        turn_planner: TurnPlanner,
        turn_validator: TurnPlanValidator,
        task_handler: TaskHandler,
        knowledge_handler: KnowledgeHandler,
        chit_chat_handler: ChitchatHandler,
        clarify_responder: ClarifyResponder,
    ):
        self.turn_planner = turn_planner
        self.turn_validator = turn_validator
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chit_chat_handler = chit_chat_handler
        self.clarify_responder = clarify_responder

    async def hand_dialogue(
        self,
        dialogue_state: DialogueState,
        user_message: UserMessage,
    ) -> ProcessResult:
        self._prepare_session(dialogue_state)
        self._begin_turn(dialogue_state, user_message)

        if user_message.type is MessageType.TEXT:
            messages = await self._handle_text_message(
                dialogue_state,
                self.turn_planner,
                self.task_handler.flows,
                self.knowledge_handler.knowledge_intents,
            )
        else:
            dialogue_state.set_focused_object(focused_object=user_message.object)
            messages = await self._handle_obj_message(
                dialogue_state,
                user_message,
                self.task_handler.flows,
            )

        dialogue_state.pending_turn.bot_messages.extend(messages)
        dialogue_state.commit_turn()

        return ProcessResult(
            resident_id=user_message.resident_id,
            message_id=user_message.message_id,
            messages=messages,
        )

    def _prepare_session(self, dialogue_state: DialogueState):
        current_session = dialogue_state.current_session()
        if current_session is None:
            dialogue_state.start_session()
            return

        now = time.time()
        if now - current_session.last_activity_at > 60 * 60:
            dialogue_state.close_session()
            dialogue_state.reset_running_state_for_new_session()
            dialogue_state.start_session()
        else:
            current_session.last_activity_at = now

    def _begin_turn(self, dialogue_state: DialogueState, user_message: UserMessage):
        return dialogue_state.begin_turn(user_message)

    async def _handle_text_message(
        self,
        dialogue_state: DialogueState,
        turn_planner: TurnPlanner,
        flows: FlowList,
        intents: Dict[str, KnowledgeIntent],
    ) -> list[BotMessage]:
        exit_messages = self._try_handle_runtime_exit(dialogue_state)
        if exit_messages is not None:
            return exit_messages

        turn_plan = await turn_planner.predict(dialogue_state, flows, intents)
        validated = self.turn_validator.validate(
            dialogue_state,
            turn_plan=turn_plan,
            flows=flows,
            intents=intents,
        )

        if not validated.valid:
            return await self.clarify_responder.respond(
                state=dialogue_state,
                reason=validated.reason,
            )

        if turn_plan.task is not None:
            return await self.task_handler.handle(
                state=dialogue_state,
                commands=turn_plan.task.commands,
            )

        if turn_plan.knowledge is not None:
            return self.knowledge_handler.handle(
                state=dialogue_state,
                turn_plan=turn_plan.knowledge,
            )

        return self.chit_chat_handler.handle(state=dialogue_state)

    async def _handle_obj_message(
        self,
        dialogue_state: DialogueState,
        user_message: UserMessage,
        flows: FlowList,
    ) -> list[BotMessage]:
        commands = self._resolve_object_commands(
            messages=user_message,
            state=dialogue_state,
            flows=flows,
        )

        if commands:
            return await self.task_handler.handle(
                state=dialogue_state,
                commands=commands,
            )

        if dialogue_state.active_task is not None:
            return await self.task_handler.handle(
                state=dialogue_state,
                commands=commands,
            )

        return await self.clarify_responder.respond(
            state=dialogue_state,
            reason=ClarifyReason.OBJECT_REQUIRES_INTENT,
        )

    def _resolve_object_commands(
        self,
        messages: UserMessage,
        state: DialogueState,
        flows: FlowList,
    ) -> list[Command]:
        user_object = messages.object
        if not user_object:
            return []

        user_object_type = user_object.type

        if user_object_type == "work_order":
            if self._flow_has_unfilled_collect_slot(state, flows, "work_order_id"):
                return [SetSlotsCommand(command="set_slots", slots={"work_order_id": user_object.id})]
            return []

        if user_object_type == "service_item":
            if self._flow_has_unfilled_collect_slot(state, flows, "service_item_id"):
                return [SetSlotsCommand(command="set_slots", slots={"service_item_id": user_object.id})]
            return []

        return []

    def _flow_has_unfilled_collect_slot(
        self,
        state: DialogueState,
        flows: FlowList,
        slot_name: str,
    ) -> bool:
        active_task = state.active_task
        if active_task is None:
            return False

        flow = flows.get_flow_by_id(active_task.flow_id)
        if not flow:
            return False

        if active_task.slots.get(slot_name):
            return False

        for step in flow.steps:
            if isinstance(step, CollectedFlowStep) and step.slot_name == slot_name:
                return True

        return False

    def _try_handle_runtime_exit(self, dialogue_state: DialogueState) -> list[BotMessage] | None:
        pending_turn = dialogue_state.pending_turn
        if pending_turn is None:
            return None

        user_message = pending_turn.user_message
        if user_message.type is not MessageType.TEXT:
            return None

        focused_object = dialogue_state.focused_object
        had_focused_object = focused_object is not None
        had_task_context = (
            dialogue_state.active_task is not None
            or bool(dialogue_state.paused_tasks)
            or dialogue_state.active_system_task is not None
        )
        normalized_text = self._normalize_exit_text(user_message.text)
        if not self._is_runtime_exit_request(normalized_text):
            return None

        if not dialogue_state.has_runtime_state():
            return [BotMessage(text="当前没有需要退出的内容，你可以直接告诉我新的需求。")]

        dialogue_state.clear_runtime_state()
        if had_task_context:
            return [BotMessage(text="好的，这段办理流程我先帮你停在这里。你可以直接说新的需求。")]

        if had_focused_object:
            object_title = focused_object.title or focused_object.id
            object_label = "这个工单" if focused_object.type == "work_order" else "这个项目"
            return [BotMessage(text=f"好的，{object_label}“{object_title}”我先不继续跟了。你可以重新选别的，或者直接问我新的问题。")]

        return [BotMessage(text="好的，当前上下文我先帮你清掉了。你可以重新开始。")]

    @staticmethod
    def _normalize_exit_text(text: str | None) -> str:
        normalized = (text or "").strip().lower()
        return re.sub(r"[\s,，。.!！？?？:：;；、】【\[\]（）()\"“”'‘’\-]+", "", normalized)

    def _is_runtime_exit_request(self, normalized_text: str) -> bool:
        if not normalized_text:
            return False

        if normalized_text in self.EXIT_RUNTIME_TEXTS:
            return True

        if any(phrase in normalized_text for phrase in self.EXIT_RUNTIME_PHRASES):
            return True

        if len(normalized_text) <= 12 and any(
            keyword in normalized_text
            for keyword in ("取消", "退出", "结束", "重置", "重来", "重新开始", "清空")
        ):
            return True

        prefixes = ("退出当前", "取消当前", "结束当前", "清空当前", "重置当前")
        return any(normalized_text.startswith(prefix) for prefix in prefixes)
