from atguigu.domain.messages import BotMessage, FocusedObject
from atguigu.domain.state import ConversationState, DialogueState
from atguigu.engine.state_decision.models import ContextDecision, TaskTransitionOutcome, TextTurnContext
from atguigu.engine.state_decision.semantic_classifier import TurnSemanticClassifier
from atguigu.engine.state_decision.semantic_kind import SemanticKind
from atguigu.engine.state_decision.state_machine import DialogueStateMachine
from atguigu.plan.turn_plan import ClarifyContext, RuntimeDirectiveTurnPlan, TurnPlan
from atguigu.task.command.models import CancelFlowCommand, Command, ResumeFlowCommand, SetSlotsCommand, StartFlowCommand


class StateDecisionEngine:
    def __init__(self) -> None:
        """
        功能：构造状态决策引擎，统一处理文本轮次语义判断、路由决策和状态迁移。

        输入：
        - 无。

        输出：
        - 无返回值；初始化语义分类器和状态机。

        调用情况：
        - 由 `DialogueEngine.__init__()` 创建。

        副作用：
        - 无。
        """
        self.semantic_classifier = TurnSemanticClassifier()
        self.state_machine = DialogueStateMachine()

    def build_text_context(
        self,
        dialogue_state: DialogueState,
        turn_plan: TurnPlan,
    ) -> TextTurnContext:
        """
        功能：把协议通过后的 TurnPlan 解释成可执行的文本轮次上下文。

        输入：
        - dialogue_state: 当前运行时状态。
        - turn_plan: 协议闸门通过后的 TurnPlan。

        输出：
        - TextTurnContext: 包含 turn_plan、语义类型和上下文决策的统一对象。

        调用情况：
        - 由 `TextTurnHandler.handle()` 调用。

        副作用：
        - 无；这里只做决策构造，不直接写状态。
        """
        semantic_kind = self.semantic_classifier.classify(dialogue_state, turn_plan)
        return TextTurnContext(
            turn_plan=turn_plan,
            semantic_kind=semantic_kind,
            decision=self._build_context_decision(
                dialogue_state,
                turn_plan,
                semantic_kind=semantic_kind,
            ),
        )

    @staticmethod
    def should_execute_task_turn(turn_context: TextTurnContext) -> bool:
        """
        功能：判断当前文本轮次是否应该进入 task 执行器。

        输入：
        - turn_context: 状态决策层构造的文本上下文。

        输出：
        - bool: 只有 task 决策且语义属于只读查询/业务办理时返回 True。

        调用情况：
        - 由 `TextTurnHandler._execute_context()` 调用。

        副作用：
        - 无。
        """
        return (
            turn_context.decision.kind == "task"
            and turn_context.semantic_kind in {
                SemanticKind.READ_ONLY_QUERY,
                SemanticKind.BUSINESS_TASK,
            }
        )

    def apply_clarify(
        self,
        dialogue_state: DialogueState,
        *,
        event: str,
        clarify_context: ClarifyContext | None = None,
        reason: str | None = None,
    ) -> None:
        """
        功能：把当前轮次显式标记为 clarify 路由并更新状态。

        输入：
        - dialogue_state: 当前运行时状态。
        - event: 本次澄清事件名。
        - clarify_context: 可选的澄清上下文对象。
        - reason: 可选的澄清原因；为空时优先从 clarify_context 推断。

        输出：
        - 无返回值。

        调用情况：
        - 由 `TextTurnHandler`、`ObjectTurnHandler` 调用。

        副作用：
        - 会更新 `last_route`、`conversation_state` 和 `last_transition`。
        """
        clarify_reason = reason
        if clarify_reason is None and clarify_context is not None and clarify_context.reason is not None:
            clarify_reason = clarify_context.reason.value

        self.state_machine.apply_route_decision(
            dialogue_state,
            ContextDecision(
                kind="clarify",
                event=event,
                reason=clarify_reason,
                semantic_kind=SemanticKind.SOCIAL_OR_CLARIFY.value,
            ),
        )

    def apply_route_decision(
        self,
        dialogue_state: DialogueState,
        decision: ContextDecision,
    ) -> None:
        """
        功能：把普通路由决策交给状态机落到 DialogueState。

        输入：
        - dialogue_state: 当前运行时状态。
        - decision: 当前轮次上下文决策。

        输出：
        - 无返回值。

        调用情况：
        - 由文本轨在 knowledge / chitchat 分支调用。

        副作用：
        - 会更新 `last_route`、`conversation_state` 和 `last_transition`。
        """
        self.state_machine.apply_route_decision(dialogue_state, decision)

    def begin_task_execution(
        self,
        dialogue_state: DialogueState,
        *,
        route_event: str,
        route_reason: str | None,
        semantic_kind: str | None,
    ) -> None:
        """
        功能：在 task 真正执行前，把当前轮次登记成 task 路由。

        输入：
        - dialogue_state: 当前运行时状态。
        - route_event: 进入 task 的事件名。
        - route_reason: 进入 task 的原因说明。
        - semantic_kind: 当前轮次的语义分类。

        输出：
        - 无返回值。

        调用情况：
        - 由 `TaskCommandExecutor.execute()` 调用。

        副作用：
        - 会更新 `last_route` 和 `conversation_state`。
        """
        self.state_machine.apply_route_decision(
            dialogue_state,
            ContextDecision(
                kind="task",
                event=route_event,
                reason=route_reason,
                semantic_kind=semantic_kind,
            ),
        )

    def finalize_task_execution(
        self,
        dialogue_state: DialogueState,
        *,
        commands: list[Command],
        source_event: str,
        default_reason: str | None,
        semantic_kind: str | None,
    ) -> None:
        """
        功能：根据 task 执行后的最新状态，总结 task outcome 并收口状态迁移。

        输入：
        - dialogue_state: 已被 task handler 修改过的运行时状态。
        - commands: 本轮执行过的 task 命令列表。
        - source_event: 构造 outcome 事件名前缀。
        - default_reason: 默认原因说明。
        - semantic_kind: 当前轮次语义分类。

        输出：
        - 无返回值。

        调用情况：
        - 由 `TaskCommandExecutor.execute()` 在 task 执行后调用。

        副作用：
        - 会更新 `last_task_outcome`、`conversation_state` 和 `last_transition`。
        """
        self.state_machine.finalize_task_transition(
            dialogue_state,
            outcome=self._build_task_transition_outcome(
                dialogue_state,
                commands=commands,
                source_event=source_event,
                default_reason=default_reason,
                semantic_kind=semantic_kind,
            ),
        )

    @staticmethod
    def describe_focused_object(user_object: FocusedObject | None) -> str | None:
        """
        功能：把 focused object 压缩成用于记录 reason 的短文本。

        输入：
        - user_object: 可能为空的聚焦对象。

        输出：
        - str | None: 形如 `type:id` 的对象标识；无对象时返回 None。

        调用情况：
        - 由对象轨、知识轨和 task outcome 构造分支复用。

        副作用：
        - 无。
        """
        if user_object is None:
            return None
        return f"{user_object.type}:{user_object.id}"

    def execute_runtime_directive(
        self,
        dialogue_state: DialogueState,
        directive: RuntimeDirectiveTurnPlan | None,
    ) -> list[BotMessage]:
        """
        功能：执行 runtime directive，目前主要支持退出当前上下文。

        输入：
        - dialogue_state: 当前运行时状态。
        - directive: runtime directive 计划，可为空。

        输出：
        - list[BotMessage]: 对用户的反馈消息列表。

        调用情况：
        - 由 `TextTurnHandler._execute_context()` 的 directive 分支调用。

        副作用：
        - 可能重置 runtime state，并更新 route / state transition。
        """
        if directive is None:
            return [BotMessage(text="当前没有需要处理的系统指令。你可以直接说新的需求。")]
        if not directive.is_exit_runtime():
            return [BotMessage(text="这次的系统指令我还没法处理。你可以直接重新说新的需求。")]
        return self._execute_exit_runtime(dialogue_state)

    def _build_context_decision(
        self,
        dialogue_state: DialogueState,
        turn_plan: TurnPlan,
        *,
        semantic_kind: SemanticKind,
    ) -> ContextDecision:
        """
        功能：把 TurnPlan 归纳成知识、任务、闲聊或 directive 的显式上下文决策。

        输入：
        - dialogue_state: 当前运行时状态。
        - turn_plan: 协议闸门通过后的 TurnPlan。
        - semantic_kind: 当前轮次的语义分类。

        输出：
        - ContextDecision: 文本轨执行前使用的统一决策对象。

        调用情况：
        - 由 `build_text_context()` 调用。

        副作用：
        - 无。
        """
        directive_decision = self._build_runtime_directive_decision(turn_plan)
        if directive_decision is not None:
            return directive_decision

        if turn_plan.task is not None:
            return ContextDecision(
                kind="task",
                event="task_turn_selected",
                reason=self._describe_task_transition(
                    dialogue_state,
                    turn_plan.task.commands,
                ),
                semantic_kind=semantic_kind.value,
            )

        if turn_plan.knowledge is not None:
            return ContextDecision(
                kind="knowledge",
                event="knowledge_turn_selected",
                reason=self.describe_focused_object(dialogue_state.focused_object),
                semantic_kind=semantic_kind.value,
            )

        return ContextDecision(
            kind="chitchat",
            event="chitchat_turn_selected",
            reason=semantic_kind.value,
            semantic_kind=semantic_kind.value,
        )

    @staticmethod
    def _build_runtime_directive_decision(
        turn_plan: TurnPlan,
    ) -> ContextDecision | None:
        """
        功能：从 TurnPlan 中提取 runtime directive 决策。

        输入：
        - turn_plan: 当前轮次计划。

        输出：
        - ContextDecision | None: 存在 exit_runtime 指令时返回 directive 决策，否则返回 None。

        调用情况：
        - 由 `_build_context_decision()` 调用。

        副作用：
        - 无。
        """
        directive = turn_plan.directive
        if directive is None or not directive.is_exit_runtime():
            return None

        return ContextDecision(
            kind="directive",
            event="runtime_exit_requested",
            reason="planner_directive",
            semantic_kind=SemanticKind.RUNTIME_CONTROL.value,
        )

    @staticmethod
    def _describe_task_transition(
        dialogue_state: DialogueState,
        commands: list[Command],
    ) -> str:
        """
        功能：把当前 task 命令列表压缩成一条可读的转换摘要。

        输入：
        - dialogue_state: 当前运行时状态。
        - commands: 当前轮次的 task 命令列表。

        输出：
        - str: 例如 `start:flow`、`switch:a->b`、`resume:latest` 这样的摘要文本。

        调用情况：
        - 由 `_build_context_decision()` 和 `_build_task_transition_outcome()` 调用。

        副作用：
        - 无。
        """
        active_flow_id = dialogue_state.active_task.flow_id if dialogue_state.active_task is not None else None

        cancel_command = next((command for command in commands if isinstance(command, CancelFlowCommand)), None)
        if cancel_command is not None:
            return f"cancel:{active_flow_id or 'none'}"

        resume_command = next((command for command in commands if isinstance(command, ResumeFlowCommand)), None)
        if resume_command is not None:
            return f"resume:{resume_command.flow or 'latest'}"

        start_command = next((command for command in commands if isinstance(command, StartFlowCommand)), None)
        if start_command is not None:
            if active_flow_id is None:
                return f"start:{start_command.flow}"
            if active_flow_id == start_command.flow:
                return f"continue:{start_command.flow}"
            return f"switch:{active_flow_id}->{start_command.flow}"

        set_slots_command = next((command for command in commands if isinstance(command, SetSlotsCommand)), None)
        if set_slots_command is not None:
            slot_names = ",".join(sorted(set_slots_command.slots.keys()))
            return f"set_slots:{slot_names}"

        return "task"

    def _build_task_transition_outcome(
        self,
        dialogue_state: DialogueState,
        *,
        commands: list[Command],
        source_event: str,
        default_reason: str | None,
        semantic_kind: str | None,
    ) -> TaskTransitionOutcome:
        """
        功能：根据 task 执行后的状态，推导本轮 task outcome。

        输入：
        - dialogue_state: task handler 执行后的状态。
        - commands: 本轮命令列表。
        - source_event: 构造 outcome 事件名前缀。
        - default_reason: 默认原因说明。
        - semantic_kind: 当前语义分类。

        输出：
        - TaskTransitionOutcome: 等待补槽、系统流活跃、业务任务活跃、完成回焦点、完成归空态等结果。

        调用情况：
        - 由 `finalize_task_execution()` 调用。

        副作用：
        - 无；只做 outcome 归纳。
        """
        main_action = self._describe_task_transition(dialogue_state, commands)

        if dialogue_state.active_system_task is not None:
            if dialogue_state.active_system_task.flow_id == "system_collect_information":
                slot_name = getattr(dialogue_state.active_system_task, "slot_name", None)
                return TaskTransitionOutcome(
                    kind="waiting_for_slot",
                    event=f"{source_event}_waiting_for_slot",
                    reason=slot_name or default_reason or main_action,
                    semantic_kind=semantic_kind,
                )

            return TaskTransitionOutcome(
                kind="system_flow_active",
                event=f"{source_event}_system_flow_active",
                reason=dialogue_state.active_system_task.flow_id,
                semantic_kind=semantic_kind,
            )

        if dialogue_state.active_task is not None:
            return TaskTransitionOutcome(
                kind="active_task",
                event=f"{source_event}_task_active",
                reason=dialogue_state.active_task.flow_id,
                semantic_kind=semantic_kind,
            )

        if dialogue_state.focused_object is not None:
            return TaskTransitionOutcome(
                kind="completed_with_focus",
                event=f"{source_event}_task_completed_with_focus",
                reason=default_reason or main_action,
                semantic_kind=semantic_kind,
            )

        return TaskTransitionOutcome(
            kind="completed_to_idle",
            event=f"{source_event}_task_completed_to_idle",
            reason=default_reason or main_action,
            semantic_kind=semantic_kind,
        )

    def _execute_exit_runtime(self, dialogue_state: DialogueState) -> list[BotMessage]:
        """
        功能：执行“退出当前上下文”指令，并给出用户可理解的反馈。

        输入：
        - dialogue_state: 当前运行时状态。

        输出：
        - list[BotMessage]: 退出后的反馈消息。

        调用情况：
        - 由 `execute_runtime_directive()` 调用。

        副作用：
        - 会重置 active_task / active_system_task / paused_tasks / focused_object 等 runtime state。
        """
        focused_object = dialogue_state.focused_object
        had_focused_object = focused_object is not None
        had_task_context = (
            dialogue_state.active_task is not None
            or bool(dialogue_state.paused_tasks)
            or dialogue_state.active_system_task is not None
        )

        if not dialogue_state.has_runtime_state():
            # 没有可退出的运行时上下文时，只记录一次 noop exit。
            dialogue_state.record_route(
                kind="chitchat",
                event="exit_without_runtime_state",
                reason="noop_exit",
                semantic_kind=SemanticKind.RUNTIME_CONTROL.value,
            )
            dialogue_state.transition_to(
                next_state=ConversationState.IDLE,
                event="exit_without_runtime_state",
                reason="noop_exit",
            )
            return [BotMessage(text="当前没有需要退出的内容。你可以直接重新说新的需求。")]

        reason = "task_context" if had_task_context else "focused_object" if had_focused_object else "runtime_state"
        dialogue_state.record_route(
            kind="chitchat",
            event="runtime_exit_requested",
            reason=reason,
            semantic_kind=SemanticKind.RUNTIME_CONTROL.value,
        )
        dialogue_state.reset_runtime_state(
            event="runtime_exit_requested",
            reason=reason,
        )

        if had_task_context:
            return [BotMessage(text="好的，当前这段办理流程已经退出了。你可以重新说新的需求。")]

        if had_focused_object and focused_object is not None:
            object_label = "这个工单" if focused_object.type == "work_order" else "这个项目"
            return [BotMessage(text=f"好的，{object_label}已经退出了，我先不继续跟进。你可以重新选别的，或者直接说新的需求。")]

        return [BotMessage(text="好的，当前上下文已经退出了。你可以重新开始。")]
