from __future__ import annotations

from atguigu.domain.state import DialogueState
from atguigu.plan.read_only_resolver import ReadOnlyResolver
from atguigu.plan.turn_plan import (
    RuntimeDirectiveAction,
    RuntimeDirectiveTurnPlan,
    TaskTurnPlan,
    TurnPlan,
)
from atguigu.task.command.models import CancelFlowCommand, SetSlotsCommand


CONFIRM_STAGE_STEP_ID = "ask_complaint_confirm"
CONFIRM_SLOT_NAME = "complaint_confirm"
EXIT_PHRASES = {
    "算了",
    "先取消",
    "取消",
    "先全部取消",
    "全部取消",
    "不提交了",
    "先不继续",
    "不继续了",
    "退出",
    "不办了",
}


class TurnPlanNormalizer:
    """Normalize planner output into the runtime protocol shape."""

    def __init__(self, read_only_resolver: ReadOnlyResolver | None = None) -> None:
        self._read_only_resolver = read_only_resolver or ReadOnlyResolver()

    def normalize(
        self,
        dialogue_state: DialogueState,
        turn_plan: TurnPlan,
    ) -> TurnPlan:
        if turn_plan.directive is not None:
            return turn_plan

        exit_directive = self._build_exit_runtime_directive_if_needed(dialogue_state, turn_plan)
        if exit_directive is not None:
            return exit_directive

        compatibility_resolution = self._read_only_resolver.resolve_compatibility_rewrite(
            dialogue_state,
            turn_plan,
        )
        if compatibility_resolution.rewritten_plan is not None:
            return compatibility_resolution.rewritten_plan

        fallback_resolution = self._read_only_resolver.resolve_service_item_fallback(
            dialogue_state,
            turn_plan,
        )
        if fallback_resolution.rewritten_plan is not None:
            return fallback_resolution.rewritten_plan

        return turn_plan

    def _build_exit_runtime_directive_if_needed(
        self,
        dialogue_state: DialogueState,
        turn_plan: TurnPlan,
    ) -> TurnPlan | None:
        if self._should_convert_confirm_stage_exit(dialogue_state, turn_plan):
            return self._build_exit_runtime_directive()

        if self._should_convert_cancel_to_exit(dialogue_state, turn_plan.task):
            return self._build_exit_runtime_directive()

        return None

    @staticmethod
    def _build_exit_runtime_directive() -> TurnPlan:
        return TurnPlan(
            directive=RuntimeDirectiveTurnPlan(action=RuntimeDirectiveAction.EXIT_RUNTIME.value),
        )

    @staticmethod
    def _should_convert_cancel_to_exit(
        dialogue_state: DialogueState,
        task_plan: TaskTurnPlan | None,
    ) -> bool:
        if task_plan is None or len(task_plan.commands) != 1:
            return False
        if not dialogue_state.has_runtime_state():
            return False
        return isinstance(task_plan.commands[0], CancelFlowCommand)

    @classmethod
    def _should_convert_confirm_stage_exit(
        cls,
        dialogue_state: DialogueState,
        turn_plan: TurnPlan,
    ) -> bool:
        task_plan = turn_plan.task
        active_task = dialogue_state.active_task
        user_text = cls._get_pending_user_text(dialogue_state)

        if not user_text or task_plan is None or active_task is None:
            return False
        if active_task.step_id != CONFIRM_STAGE_STEP_ID:
            return False
        if not cls._has_confirm_stage_signal(dialogue_state, task_plan):
            return False

        normalized_text = cls._normalize_text(user_text)
        return any(phrase in normalized_text for phrase in EXIT_PHRASES)

    @staticmethod
    def _get_pending_user_text(dialogue_state: DialogueState) -> str:
        pending_turn = dialogue_state.pending_turn
        return (pending_turn.user_message.text or "").strip() if pending_turn is not None else ""

    @staticmethod
    def _has_confirm_stage_signal(
        dialogue_state: DialogueState,
        task_plan: TaskTurnPlan,
    ) -> bool:
        active_system_task = dialogue_state.active_system_task
        slot_name = getattr(active_system_task, "slot_name", None) if active_system_task is not None else None
        return slot_name == CONFIRM_SLOT_NAME or any(
            isinstance(command, SetSlotsCommand) and CONFIRM_SLOT_NAME in command.slots
            for command in task_plan.commands
        )

    @staticmethod
    def _normalize_text(user_text: str) -> str:
        normalized = user_text.strip()
        for token in ("，", "。", "、", "；", ",", ".", " ", "\n", "\t"):
            normalized = normalized.replace(token, "")
        return normalized
