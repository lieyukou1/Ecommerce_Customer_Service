from __future__ import annotations

from dataclasses import dataclass

from atguigu.domain.state import DialogueState
from atguigu.plan.turn_plan import KnowledgeTurnPlan, TaskTurnPlan, TurnPlan
from atguigu.task.command.models import SetSlotsCommand, StartFlowCommand


HIGH_LOSS_READ_ONLY_FLOW_IDS = {
    "resident_work_orders_list_query",
    "resident_service_items_list_query",
    "work_order_status_query",
    "service_progress_tracking",
    "service_item_detail_query",
}
SERVICE_ITEM_FALLBACK_INTENT = "service_item_info"
SERVICE_ITEM_FALLBACK_STATES = {"focused_knowledge", "clarifying"}

# Compatibility-only fallback hints. These are not the primary routing contract.
WORK_ORDER_PROGRESS_HINTS = (
    "进度",
    "进展",
    "处理到哪",
    "上门",
    "安排",
    "何时",
)
WORK_ORDER_STATUS_HINTS = (
    "状态",
    "收费",
    "费用",
    "多少钱",
)
WORK_ORDER_LIST_HINTS = (
    "工单列表",
    "都有哪些工单",
    "还有哪些工单",
    "几个工单",
)
SERVICE_ITEM_LIST_HINTS = (
    "哪些服务",
    "什么服务",
    "服务项目",
    "能办什么",
    "项目列表",
)
SERVICE_ITEM_DETAIL_HINTS = (
    "详情",
    "详细",
    "全部信息",
    "状态和价格",
    "具体都做什么",
    "这个项目",
)
SERVICE_ITEM_KNOWLEDGE_ONLY_HINTS = (
    "注意事项",
    "材料要求",
    "领取方式",
    "办理地点",
    "适用",
    "规则",
    "要求",
)


@dataclass(slots=True)
class ReadOnlyResolution:
    rewritten_plan: TurnPlan | None = None
    source: str | None = None


class ReadOnlyResolver:
    """Resolve read-only requests into runtime-compatible task or knowledge plans."""

    def resolve_compatibility_rewrite(
        self,
        dialogue_state: DialogueState,
        turn_plan: TurnPlan,
    ) -> ReadOnlyResolution:
        if turn_plan.task is not None:
            return ReadOnlyResolution()
        if dialogue_state.active_task is not None or dialogue_state.active_system_task is not None:
            return ReadOnlyResolution()

        user_text = self._normalize_text(self._get_pending_user_text(dialogue_state))
        if not user_text:
            return ReadOnlyResolution()

        focused_object = dialogue_state.focused_object
        if focused_object is None:
            if not self._allows_high_loss_rewrite(turn_plan):
                return ReadOnlyResolution()
            if self._contains_any(user_text, WORK_ORDER_LIST_HINTS):
                return ReadOnlyResolution(
                    rewritten_plan=self._build_read_only_task_plan("resident_work_orders_list_query"),
                    source="compat_work_order_list",
                )
            if self._contains_any(user_text, SERVICE_ITEM_LIST_HINTS):
                return ReadOnlyResolution(
                    rewritten_plan=self._build_read_only_task_plan("resident_service_items_list_query"),
                    source="compat_service_item_list",
                )
            return ReadOnlyResolution()

        if focused_object.type == "work_order":
            if not self._allows_intent_rewrite(turn_plan, {"work_order_info"}):
                return ReadOnlyResolution()
            if not self._looks_like_work_order_runtime_query(user_text):
                return ReadOnlyResolution()
            flow_id = self._select_work_order_runtime_flow(user_text)
            return ReadOnlyResolution(
                rewritten_plan=self._build_read_only_task_plan(
                    flow_id,
                    {"work_order_id": focused_object.id},
                ),
                source="compat_work_order_runtime",
            )

        if focused_object.type == "service_item":
            if not self._allows_intent_rewrite(turn_plan, {"service_item_info"}):
                return ReadOnlyResolution()
            if not self._looks_like_service_item_detail_query(user_text):
                return ReadOnlyResolution()
            return ReadOnlyResolution(
                rewritten_plan=self._build_read_only_task_plan(
                    "service_item_detail_query",
                    {"service_item_id": focused_object.id},
                ),
                source="compat_service_item_detail",
            )

        return ReadOnlyResolution()

    def resolve_service_item_fallback(
        self,
        dialogue_state: DialogueState,
        turn_plan: TurnPlan,
    ) -> ReadOnlyResolution:
        if turn_plan.active_tracks():
            return ReadOnlyResolution()
        if dialogue_state.active_task is not None:
            return ReadOnlyResolution()

        focused_object = dialogue_state.focused_object
        if focused_object is None or focused_object.type != "service_item":
            return ReadOnlyResolution()
        if dialogue_state.conversation_state not in SERVICE_ITEM_FALLBACK_STATES:
            return ReadOnlyResolution()

        return ReadOnlyResolution(
            rewritten_plan=TurnPlan(knowledge=KnowledgeTurnPlan(intents=[SERVICE_ITEM_FALLBACK_INTENT])),
            source="compat_service_item_fallback",
        )

    @staticmethod
    def _build_read_only_task_plan(flow_id: str, slots: dict | None = None) -> TurnPlan:
        commands = [StartFlowCommand(command="start_flow", flow=flow_id)]
        if slots:
            commands.append(SetSlotsCommand(command="set_slots", slots=slots))
        return TurnPlan(task=TaskTurnPlan(commands=commands))

    @staticmethod
    def _allows_high_loss_rewrite(turn_plan: TurnPlan) -> bool:
        if turn_plan.knowledge is not None:
            return True
        return not turn_plan.active_tracks()

    @staticmethod
    def _allows_intent_rewrite(turn_plan: TurnPlan, allowed_intents: set[str]) -> bool:
        if turn_plan.knowledge is not None:
            if not turn_plan.knowledge.intents:
                return False
            return set(turn_plan.knowledge.intents).issubset(allowed_intents)
        return not turn_plan.active_tracks()

    @staticmethod
    def _looks_like_work_order_runtime_query(user_text: str) -> bool:
        return ReadOnlyResolver._contains_any(user_text, WORK_ORDER_PROGRESS_HINTS + WORK_ORDER_STATUS_HINTS)

    @staticmethod
    def _select_work_order_runtime_flow(user_text: str) -> str:
        if ReadOnlyResolver._contains_any(user_text, WORK_ORDER_PROGRESS_HINTS):
            return "service_progress_tracking"
        return "work_order_status_query"

    @staticmethod
    def _looks_like_service_item_detail_query(user_text: str) -> bool:
        if ReadOnlyResolver._contains_any(user_text, SERVICE_ITEM_KNOWLEDGE_ONLY_HINTS):
            return False
        if ReadOnlyResolver._contains_any(user_text, SERVICE_ITEM_DETAIL_HINTS):
            return True
        return "状态" in user_text and ("价格" in user_text or "收费" in user_text)

    @staticmethod
    def _contains_any(user_text: str, phrases: tuple[str, ...]) -> bool:
        return any(phrase in user_text for phrase in phrases)

    @staticmethod
    def _get_pending_user_text(dialogue_state: DialogueState) -> str:
        pending_turn = dialogue_state.pending_turn
        return (pending_turn.user_message.text or "").strip() if pending_turn is not None else ""

    @staticmethod
    def _normalize_text(user_text: str) -> str:
        normalized = user_text.strip()
        for token in (" ", "\n", "\t", "，", "。", "？", "！", ",", ".", "?", "!"):
            normalized = normalized.replace(token, "")
        return normalized
