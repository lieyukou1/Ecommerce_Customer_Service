from dataclasses import dataclass

from atguigu.domain.state import ConversationState, DialogueState
from atguigu.engine.state_decision.models import ContextDecision, TaskTransitionOutcome


@dataclass(slots=True)
class StateTransitionPlan:
    target_state: ConversationState
    event: str
    reason: str | None = None


class DialogueStateMachine:
    def apply_route_decision(
        self,
        dialogue_state: DialogueState,
        decision: ContextDecision,
    ) -> None:
        """
        功能：把一条 route decision 应用到 DialogueState。

        输入：
        - dialogue_state: 当前运行时状态。
        - decision: 已决定好的上下文路由结果。

        输出：
        - 无返回值；结果体现在 dialogue_state 的 route 和 conversation_state 更新上。

        调用情况：
        - 由 `StateDecisionEngine.apply_route_decision()`、`apply_clarify()`、`begin_task_execution()` 调用。

        副作用：
        - 会写入 `last_route`，并同步更新 `conversation_state / last_transition`。
        """
        self._record_decision(dialogue_state, decision)
        transition_plan = self._build_route_transition_plan(decision)
        self._apply_state_transition(dialogue_state, transition_plan)

    def finalize_task_transition(
        self,
        dialogue_state: DialogueState,
        *,
        outcome: TaskTransitionOutcome,
    ) -> None:
        """
        功能：根据 task 执行后的 outcome 收口状态迁移。

        输入：
        - dialogue_state: 当前运行时状态。
        - outcome: task 执行后归纳出的结果对象。

        输出：
        - 无返回值；结果体现在 task outcome 和 conversation_state 更新上。

        调用情况：
        - 由 `StateDecisionEngine.finalize_task_execution()` 调用。

        副作用：
        - 会写入 `last_task_outcome`，并同步更新 `conversation_state / last_transition`。
        """
        self._record_task_outcome(dialogue_state, outcome)
        transition_plan = self._build_transition_plan_from_task_outcome(outcome)
        self._apply_state_transition(dialogue_state, transition_plan)

    @staticmethod
    def _record_decision(
        dialogue_state: DialogueState,
        decision: ContextDecision,
    ) -> None:
        """
        功能：把路由决策写入 `last_route`。

        输入：
        - dialogue_state: 当前运行时状态。
        - decision: 当前轮次的路由决策。

        输出：
        - 无返回值。

        调用情况：
        - 由 `apply_route_decision()` 调用。

        副作用：
        - 会更新 `dialogue_state.last_route`。
        """
        dialogue_state.record_route(
            kind=decision.kind,
            event=decision.event,
            reason=decision.reason,
            semantic_kind=decision.semantic_kind,
        )

    @staticmethod
    def _build_route_transition_plan(decision: ContextDecision) -> StateTransitionPlan:
        """
        功能：根据 route decision 推导高层 conversation_state 的目标状态。

        输入：
        - decision: 当前轮次的上下文决策。

        输出：
        - StateTransitionPlan: 目标状态与事件信息。

        调用情况：
        - 由 `apply_route_decision()` 调用。

        副作用：
        - 无。
        """
        if decision.kind == "task":
            target_state = ConversationState.TRANSITIONING
        elif decision.kind == "knowledge":
            target_state = ConversationState.FOCUSED_KNOWLEDGE
        elif decision.kind == "clarify":
            target_state = ConversationState.CLARIFYING
        else:
            target_state = ConversationState.CHITCHAT

        return StateTransitionPlan(
            target_state=target_state,
            event=decision.event,
            reason=decision.reason,
        )

    @staticmethod
    def _apply_state_transition(
        dialogue_state: DialogueState,
        transition_plan: StateTransitionPlan,
    ) -> None:
        """
        功能：把状态迁移计划真正写回 DialogueState。

        输入：
        - dialogue_state: 当前运行时状态。
        - transition_plan: 已决定好的目标状态迁移计划。

        输出：
        - 无返回值。

        调用情况：
        - 由 `apply_route_decision()` 和 `finalize_task_transition()` 调用。

        副作用：
        - 会更新 `conversation_state` 和 `last_transition`。
        """
        dialogue_state.transition_to(
            transition_plan.target_state,
            event=transition_plan.event,
            reason=transition_plan.reason,
        )

    @staticmethod
    def _record_task_outcome(
        dialogue_state: DialogueState,
        outcome: TaskTransitionOutcome,
    ) -> None:
        """
        功能：把 task 执行结果写入 `last_task_outcome`。

        输入：
        - dialogue_state: 当前运行时状态。
        - outcome: task 执行结果对象。

        输出：
        - 无返回值。

        调用情况：
        - 由 `finalize_task_transition()` 调用。

        副作用：
        - 会更新 `dialogue_state.last_task_outcome`。
        """
        flow_id = dialogue_state.active_task.flow_id if dialogue_state.active_task is not None else None
        if flow_id is None and dialogue_state.active_system_task is not None:
            flow_id = dialogue_state.active_system_task.flow_id

        dialogue_state.record_task_outcome(
            kind=outcome.kind,
            flow_id=flow_id,
            reason=outcome.reason,
            semantic_kind=outcome.semantic_kind,
        )

    @staticmethod
    def _build_transition_plan_from_task_outcome(
        outcome: TaskTransitionOutcome,
    ) -> StateTransitionPlan:
        """
        功能：根据 task outcome 推导 task 执行完成后的高层状态。

        输入：
        - outcome: task 执行结果对象。

        输出：
        - StateTransitionPlan: 对应的目标状态计划。

        调用情况：
        - 由 `finalize_task_transition()` 调用。

        副作用：
        - 无。
        """
        if outcome.kind == "waiting_for_slot":
            target_state = ConversationState.CLARIFYING
        elif outcome.kind == "system_flow_active":
            target_state = ConversationState.TRANSITIONING
        elif outcome.kind == "active_task":
            target_state = ConversationState.ACTIVE_TASK
        elif outcome.kind == "completed_with_focus":
            target_state = ConversationState.FOCUSED_KNOWLEDGE
        else:
            target_state = ConversationState.IDLE

        return StateTransitionPlan(
            target_state=target_state,
            event=outcome.event,
            reason=outcome.reason,
        )
