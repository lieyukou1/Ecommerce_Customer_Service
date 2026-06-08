import time

from atguigu.chitchat.handler import ChitchatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.domain.messages import BotMessage, MessageType, ProcessResult, UserMessage
from atguigu.domain.state import DialogueState
from atguigu.engine.focus import FocusedObjectResolver
from atguigu.engine.state_decision import StateDecisionEngine
from atguigu.engine.track_execution import build_track_execution_runtime
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.protocol_gate import TurnProtocolGate
from atguigu.task.handler import TaskHandler


class DialogueEngine:
    def __init__(
        self,
        turn_planner: TurnPlanner,
        turn_protocol_gate: TurnProtocolGate,
        task_handler: TaskHandler,
        knowledge_handler: KnowledgeHandler,
        chit_chat_handler: ChitchatHandler,
        clarify_responder: ClarifyResponder,
    ):
        """
        功能：组装对话主链的顶层编排器。

        输入：
        - turn_planner: 负责调用 LLM 产出 TurnPlan。
        - turn_protocol_gate: 负责对 TurnPlan 做归一化和校验。
        - task_handler: 负责执行业务 task 命令。
        - knowledge_handler: 负责知识轨道回复。
        - chit_chat_handler: 负责闲聊轨道回复。
        - clarify_responder: 负责澄清轨道回复。

        输出：
        - 无返回值；初始化引擎内部依赖。

        调用情况：
        - 由 `engine.builder` 装配，供 `DialogueService` 长生命周期复用。

        副作用：
        - 会创建状态决策器、focus 解析器，以及文本/对象消息执行入口。
        """
        self.turn_planner = turn_planner
        self.turn_protocol_gate = turn_protocol_gate
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chit_chat_handler = chit_chat_handler
        self.clarify_responder = clarify_responder

        # 这两个组件负责统一处理状态迁移和 focused object 承接，是主链的核心控制器。
        self.state_decision = StateDecisionEngine()
        self.focus_resolver = FocusedObjectResolver()
        # 通过运行时装配器，把文本消息和对象消息的执行入口统一组装出来。
        track_execution = build_track_execution_runtime(
            turn_planner=self.turn_planner,
            turn_protocol_gate=self.turn_protocol_gate,
            task_handler=self.task_handler,
            knowledge_handler=self.knowledge_handler,
            chit_chat_handler=self.chit_chat_handler,
            clarify_responder=self.clarify_responder,
            state_decision=self.state_decision,
            focus_resolver=self.focus_resolver,
        )
        self.text_turn_handler = track_execution.text_turn_handler
        self.object_turn_handler = track_execution.object_turn_handler

    async def hand_dialogue(
        self,
        dialogue_state: DialogueState,
        user_message: UserMessage,
    ) -> ProcessResult:
        """
        功能：处理一轮用户输入，并把结果写回当前会话 turn。

        输入：
        - dialogue_state: 当前住户的完整运行时状态。
        - user_message: 本轮进入主链的领域层用户消息。

        输出：
        - ProcessResult: 本轮机器人回复及消息元数据。

        调用情况：
        - 由 `DialogueService.process_message()` 调用，是 engine 层总入口。

        副作用：
        - 会更新 session、pending_turn、history，以及对话运行时状态。
        """
        # 先确保当前住户存在可写入的会话，并处理超时会话切换。
        self._prepare_session(dialogue_state)
        # 把这条用户消息挂到 pending_turn，后续机器人回复会回填到同一 turn。
        dialogue_state.begin_turn(user_message)

        # 根据消息类型分流到文本轨或对象轨执行入口。
        messages = await self._route_turn(dialogue_state, user_message)

        # 只有 turn 仍然处于 pending 状态时，才把本轮机器人消息追加进去。
        if dialogue_state.pending_turn is not None:
            dialogue_state.pending_turn.bot_messages.extend(messages)
        # 本轮处理结束后提交 turn，写入当前 session 的 turn 列表。
        dialogue_state.commit_turn()

        return ProcessResult(
            resident_id=user_message.resident_id,
            message_id=user_message.message_id,
            messages=messages,
        )

    async def _route_turn(
        self,
        dialogue_state: DialogueState,
        user_message: UserMessage,
    ) -> list[BotMessage]:
        """
        功能：按消息类型把本轮输入分发到文本执行链或对象执行链。

        输入：
        - dialogue_state: 当前住户运行时状态。
        - user_message: 本轮领域层用户消息。

        输出：
        - list[BotMessage]: 本轮生成的机器人消息列表。

        调用情况：
        - 由 `hand_dialogue()` 在准备好 pending_turn 后调用。

        副作用：
        - 会通过下游 handler 修改对话状态、轨道状态和对象上下文。
        """
        if user_message.type is MessageType.TEXT:
            # 文本消息需要携带 flows 和 knowledge intents 进入 planner 主链。
            return await self.text_turn_handler.handle(
                dialogue_state,
                flows=self.task_handler.flows,
                intents=self.knowledge_handler.knowledge_intents,
            )

        # 对象消息不走 planner，而是直接进入对象承接与任务衔接逻辑。
        return await self.object_turn_handler.handle(
            dialogue_state,
            user_message=user_message,
            flows=self.task_handler.flows,
        )

    @staticmethod
    def _prepare_session(dialogue_state: DialogueState) -> None:
        """
        功能：保证当前对话有可用 session，并处理会话超时切换。

        输入：
        - dialogue_state: 当前住户的完整运行时状态。

        输出：
        - 无返回值；结果体现在 dialogue_state 的 session 相关字段变化上。

        调用情况：
        - 由 `hand_dialogue()` 在每轮开始时调用。

        副作用：
        - 可能创建新 session、关闭旧 session，并重置跨 session 的运行时状态。
        """
        current_session = dialogue_state.current_session()
        if current_session is None:
            # 首次对话或没有当前会话时，直接创建新会话。
            dialogue_state.start_session()
            return

        now = time.time()
        if now - current_session.last_activity_at > 60 * 60:
            # 超过 1 小时未活动时，切断旧 session，并为新会话清理运行时上下文。
            dialogue_state.close_session()
            dialogue_state.reset_running_state_for_new_session()
            dialogue_state.start_session()
            return

        # 仍处于当前会话窗口内时，仅刷新最后活跃时间。
        current_session.last_activity_at = now
