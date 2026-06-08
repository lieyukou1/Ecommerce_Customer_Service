from atguigu.chitchat.handler import ChitchatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.engine.focus import FocusedObjectResolver
from atguigu.engine.state_decision import StateDecisionEngine
from atguigu.engine.track_execution.task_command_executor import TaskCommandExecutor
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.protocol_gate import TurnProtocolGate
from atguigu.plan.turn_plan import ClarifyContext
from atguigu.task.flow.flows import FlowList


class TextTurnHandler:
    def __init__(
        self,
        *,
        turn_planner: TurnPlanner,
        turn_protocol_gate: TurnProtocolGate,
        task_executor: TaskCommandExecutor,
        knowledge_handler: KnowledgeHandler,
        chit_chat_handler: ChitchatHandler,
        clarify_responder: ClarifyResponder,
        state_decision: StateDecisionEngine,
        focus_resolver: FocusedObjectResolver,
    ) -> None:
        """
        功能：构造文本消息执行入口，串起 planner、协议闸门、状态决策和各轨执行器。

        输入：
        - turn_planner: 负责调用 LLM 产出 TurnPlan。
        - turn_protocol_gate: 负责归一化和校验 TurnPlan。
        - task_executor: 负责 task 命令的执行包装。
        - knowledge_handler: 负责知识轨回复。
        - chit_chat_handler: 负责闲聊轨回复。
        - clarify_responder: 负责澄清轨回复。
        - state_decision: 负责状态决策和状态迁移。
        - focus_resolver: 负责文本下的 focused object 切换。

        输出：
        - 无返回值；初始化文本执行入口依赖。

        调用情况：
        - 由 `build_track_execution_runtime()` 装配，供 `DialogueEngine._route_turn()` 调用。

        副作用：
        - 无；仅保存依赖引用。
        """
        self.turn_planner = turn_planner
        self.turn_protocol_gate = turn_protocol_gate
        self.task_executor = task_executor
        self.knowledge_handler = knowledge_handler
        self.chit_chat_handler = chit_chat_handler
        self.clarify_responder = clarify_responder
        self.state_decision = state_decision
        self.focus_resolver = focus_resolver

    async def handle(
        self,
        dialogue_state: DialogueState,
        *,
        flows: FlowList,
        intents: dict[str, KnowledgeIntent],
    ) -> list[BotMessage]:
        """
        功能：处理文本消息主链，完成对象切换、TurnPlan 生成、协议收口和轨道执行。

        输入：
        - dialogue_state: 当前住户的运行时状态。
        - flows: 当前可用的任务流配置集合。
        - intents: 当前可用的知识意图注册表。

        输出：
        - list[BotMessage]: 本轮文本消息最终生成的机器人回复列表。

        调用情况：
        - 由 `DialogueEngine._route_turn()` 在文本消息分支调用。

        副作用：
        - 会修改 focused object、route decision、conversation state，以及 task 相关状态。
        """
        # 文本进入 planner 前，先尝试根据文本内容切换当前 focused object。
        await self.focus_resolver.try_switch_focused_object_from_text(dialogue_state)
        # 用当前状态、flow 和知识意图构造 planner 输入，调用 LLM 得到结构化 TurnPlan。
        turn_plan = await self.turn_planner.predict(dialogue_state, flows, intents)
        # 对 planner 输出做协议层归一化和校验，避免非法 plan 直接进入执行层。
        gate_result = self.turn_protocol_gate.process(
            dialogue_state,
            turn_plan=turn_plan,
            flows=flows,
            intents=intents,
        )
        if not gate_result.accepted:
            # plan 无法执行时，直接进入澄清分支，不继续向下执行其他轨道。
            return await self._respond_validation_failure(
                dialogue_state,
                gate_result.clarify_context,
            )

        # 协议通过后，状态决策层会把 TurnPlan 解释成显式执行上下文。
        turn_context = self.state_decision.build_text_context(
            dialogue_state,
            gate_result.turn_plan,
        )
        return await self._execute_context(dialogue_state, turn_context)

    async def _respond_validation_failure(
        self,
        dialogue_state: DialogueState,
        clarify_context: ClarifyContext | None,
    ) -> list[BotMessage]:
        """
        功能：把协议校验失败统一降级成澄清回复。

        输入：
        - dialogue_state: 当前运行时状态。
        - clarify_context: 校验失败后给出的澄清上下文。

        输出：
        - list[BotMessage]: 澄清轨生成的机器人回复。

        调用情况：
        - 由 `handle()` 在协议闸门拒绝 TurnPlan 时调用。

        副作用：
        - 会把当前 route 和记为 clarify，并把 conversation_state 切到澄清态。
        """
        # 先把这轮失败记录成 clarify 路由，再让 responder 输出对应澄清话术。
        self.state_decision.apply_clarify(
            dialogue_state,
            event="validation_failed",
            clarify_context=clarify_context,
        )
        return await self.clarify_responder.respond(
            state=dialogue_state,
            clarify_context=clarify_context,
        )

    async def _execute_context(
        self,
        dialogue_state: DialogueState,
        turn_context,
    ) -> list[BotMessage]:
        """
        功能：根据状态决策结果，把文本消息真正分发到 directive / task / knowledge / chitchat 轨道。

        输入：
        - dialogue_state: 当前运行时状态。
        - turn_context: 状态决策层输出的文本轮次上下文。

        输出：
        - list[BotMessage]: 对应轨道生成的回复列表。

        调用情况：
        - 由 `handle()` 在协议闸门通过后调用。

        副作用：
        - 会根据不同分支修改 route、task outcome、conversation state 等字段。
        """
        turn_plan = turn_context.turn_plan
        decision = turn_context.decision

        if decision.kind == "directive":
            # runtime directive 直接由状态决策层执行，例如退出当前上下文。
            return self.state_decision.execute_runtime_directive(dialogue_state, turn_plan.directive)

        if self.state_decision.should_execute_task_turn(turn_context):
            # task 轨进入统一任务执行包装器，由它负责前后状态迁移和 task handler 调用。
            return await self.task_executor.execute(
                dialogue_state,
                commands=turn_plan.task.commands,
                route_event=decision.event,
                route_reason=decision.reason,
                source_event="task",
                default_reason=decision.reason,
                semantic_kind=decision.semantic_kind,
            )

        if decision.kind == "knowledge":
            # knowledge 轨先落 route，再交给知识处理器生成回复。
            self.state_decision.apply_route_decision(dialogue_state, decision)
            return self.knowledge_handler.handle(
                state=dialogue_state,
                turn_plan=turn_plan.knowledge,
            )

        # 剩余文本路径统一视作 chitchat，同样先更新 route 再输出闲聊回复。
        self.state_decision.apply_route_decision(dialogue_state, decision)
        return self.chit_chat_handler.handle(state=dialogue_state)
