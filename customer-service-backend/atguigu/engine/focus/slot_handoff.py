from atguigu.domain.messages import UserMessage
from atguigu.domain.state import DialogueState
from atguigu.task.command.models import Command, SetSlotsCommand
from atguigu.task.flow.flows import FlowList
from atguigu.task.flow.steps import CollectedFlowStep


class ObjectSlotHandoff:
    """
    功能：把对象消息转成当前任务可消费的补槽命令。
    """

    def resolve_commands(
        self,
        *,
        user_message: UserMessage,
        dialogue_state: DialogueState,
        flows: FlowList,
    ) -> list[Command]:
        """
        功能：判断对象消息是否可以直接承接成当前任务的补槽命令。

        输入：
        - user_message: 当前对象消息。
        - dialogue_state: 当前运行时状态。
        - flows: 当前可用 flow 列表。

        输出：
        - list[Command]: 命中承接条件时返回 `SetSlotsCommand`，否则返回空列表。

        调用情况：
        - `FocusedObjectResolver.resolve_object_commands()`

        副作用：
        - 无；只构造命令对象。
        """
        user_object = user_message.object
        if user_object is None:
            return []

        # 对象消息只做“当前 collect 槽位已经明确需要某对象 ID”这一类窄承接，不负责新开任务。
        if user_object.type == "work_order" and self._flow_has_unfilled_collect_slot(
            dialogue_state,
            flows,
            "work_order_id",
        ):
            return [SetSlotsCommand(command="set_slots", slots={"work_order_id": user_object.id})]

        if user_object.type == "service_item" and self._flow_has_unfilled_collect_slot(
            dialogue_state,
            flows,
            "service_item_id",
        ):
            return [SetSlotsCommand(command="set_slots", slots={"service_item_id": user_object.id})]

        return []

    def _flow_has_unfilled_collect_slot(
        self,
        dialogue_state: DialogueState,
        flows: FlowList,
        slot_name: str,
    ) -> bool:
        """
        功能：判断当前 active task 是否存在某个尚未填充的 collect slot。

        输入：
        - dialogue_state: 当前运行时状态。
        - flows: 当前可用 flow 列表。
        - slot_name: 要检查的槽位名。

        输出：
        - bool: 当前任务存在该 collect slot 且尚未填写时返回 True。

        调用情况：
        - `resolve_commands()`

        副作用：
        - 无。
        """
        active_task = dialogue_state.active_task
        if active_task is None:
            return False

        flow = flows.get_flow_by_id(active_task.flow_id)
        if flow is None or active_task.slots.get(slot_name):
            return False

        # 这里只判断“flow 里是否定义过这个 collect step”，具体推进仍由 FlowExecutor 负责。
        for step in flow.steps:
            if isinstance(step, CollectedFlowStep) and step.slot_name == slot_name:
                return True

        return False
