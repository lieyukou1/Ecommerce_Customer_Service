from dataclasses import asdict

from atguigu.domain.contexts import CollectedSystemContext
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import ActionResult
from atguigu.task.action.runner import ActionRunner, ActionCall
from atguigu.task.flow.flows import FlowList
from atguigu.task.flow.links import FlowStepLink, StaticLink, ConditionalLink, FallbackLink
from atguigu.task.flow.steps import FlowStep, StartedFlowStep, CollectedFlowStep, EndFlowStep, ActionFlowStep


class FlowExecutor:
    """
    流程执行器：推进yaml中定义的业务任务流程以及系统任务流程
    """

    async def run_task(self,
                       state: DialogueState,
                       flows: FlowList,
                       action_runner: ActionRunner):
        messages: list[BotMessage] = []

        while True:

            action_call: ActionCall = self._advance_until_action(state, flows)

            if action_call.action_name == "action_listen":
                break
            else:
                action_result: ActionResult = await action_runner.run(action_call, state)
                state.set_slots(action_result.slot_updates)
                messages.extend(action_result.messages)

        return messages

    def _advance_until_action(self,
                              state: DialogueState,
                              flows: FlowList) -> ActionCall:
        while True:

            # 1.获取当前时刻的上下文
            current_active_task = state.current_active_task()
            if current_active_task is None:
                return ActionCall(action_name="action_listen")

            # 2.获取上下文中的流程ID
            flow_id = current_active_task.flow_id

            # 3.获取上下文中的流程对象
            flow = flows.get_flow_by_id(flow_id)

            # 4.获取上下文中的流程对象对应的step
            step = flow.get_step_by_id(current_active_task.step_id)

            # 5.运行当前step
            action_call: ActionCall | None = self._run_step(state, step, flows)

            # 6.如果step的类型是action则推出，否则继续循环
            if action_call is not None:
                return action_call

    def _run_step(self,
                  state: DialogueState,
                  step: FlowStep,
                  flows: FlowList) -> ActionCall | None:

        if isinstance(step, StartedFlowStep):
            return self._run_start_step(step, state)

        if isinstance(step, CollectedFlowStep):
            return self._run_collect_slots_step(step, state, flows)

        if isinstance(step, EndFlowStep):
            return self._run_end_step(state)

        if isinstance(step, ActionFlowStep):
            return self._run_action_step(step, state)

    def _run_start_step(self,
                        step: StartedFlowStep,
                        state: DialogueState) -> None:
        # 1.推进下一步
        self._advance_next_step(state, step)

        # 2.退出
        return None

    def _advance_next_step(self,
                           state: DialogueState,
                           step: FlowStep):
        # 1.寻找下一条边

        next_step_id = self._select_next_step(step, state)

        # 2.将下一步的step_id更新到state中

        state.current_active_task().step_id = next_step_id

    def _select_next_step(self,
                          step: FlowStep,
                          state: DialogueState) -> str:
        links: list[FlowStepLink] = step.next

        for link in links:

            if isinstance(link, StaticLink):
                return link.target

            if isinstance(link, ConditionalLink):
                if self._eval_condition(link.condition, state):
                    return link.target

            if isinstance(link, FallbackLink):
                return link.target

    def _eval_condition(self,
                        condition: str,
                        state: DialogueState) -> bool:

        data = {
            "slots": state.active_task.slots,
            "context": asdict(state.current_active_task())
        }

        return bool(eval(condition, {}, data))

    def _run_collect_slots_step(self,
                                step: CollectedFlowStep,
                                state: DialogueState,
                                flows: FlowList) -> ActionCall | None:

        # 1.尝试自动补槽位
        self._try_fill_slot_from_focused_object(state, step)

        # 2.判断槽位是否已经被填写
        if state.active_task.slots.get(step.slot_name):

            # 2.1判断槽位是否有验证
            if step.validate:

                # 2.1.1判断槽位能否经过验证
                if self._eval_condition(condition=step.validate.condition, state=state):

                    self._advance_next_step(state, step)
                    return None
                else:

                    # 2.1.2.1将原有的不符合条件的槽位清空
                    state.remove_slot(slot_name=step.slot_name)
                    # 2.1.2.2判断是否存在failure_response
                    if step.validate.failure_response:
                        return ActionCall(
                            action_name="action_response",
                            action_kwargs=asdict(step.validate.failure_response)
                        )
                    else:
                        return ActionCall(
                            action_name="action_response",
                            action_kwargs={"text": "您填写的信息有误，请您重新再填"}
                        )
            else:

                # 无验证的不再返回，直接进行下一步流程
                self._advance_next_step(state, step)
                return None
        else:

            # 槽位未被填写，填槽位
            state.start_active_system_task(
                CollectedSystemContext(
                    flow_id="system_collect_information",
                    step_id=flows.get_flow_by_id("system_collect_information").start_step().id,
                    slot_name=step.slot_name,
                    response=asdict(step.response)
                )
            )
            return None

    def _try_fill_slot_from_focused_object(self,
                                           state: DialogueState,
                                           step: CollectedFlowStep):

        if state.focused_object is None:
            return

        focused_object = state.focused_object
        attributes = focused_object.attributes
        slot_name = step.slot_name

        if focused_object.type == "work_order":
            slot_value = {
                "work_order_id": focused_object.id,
                "work_order_status_hint": attributes.get("status"),
                "work_order_summary_hint": attributes.get("summary") or focused_object.title,
                "appointment_time_hint": attributes.get("appointment_time"),
                "work_order_amount_hint": attributes.get("amount"),
            }.get(slot_name)

            if slot_value is not None:
                state.set_slots({slot_name: slot_value})
            return

        if focused_object.type == "service_item":
            slot_value = {
                "service_item_id": focused_object.id,
                "service_item_status_hint": attributes.get("service_status"),
                "service_item_description_hint": attributes.get("description") or focused_object.title,
                "service_item_price_hint": attributes.get("price"),
            }.get(slot_name)

            if slot_value is not None:
                state.set_slots({slot_name: slot_value})

    def _run_end_step(self,
                      state: DialogueState) -> None:
        if state.active_system_task:
            state.end_active_system_task()
            return None

        if state.active_task:
            state.end_active_task()
            return None

    def _run_action_step(self,
                         step: ActionFlowStep,
                         state: DialogueState) -> ActionCall:
        self._advance_next_step(state, step)
        return self._build_action_call(state, step)

    def _build_action_call(self,
                           state: DialogueState,
                           step: ActionFlowStep) -> ActionCall:
        action_name = step.action

        action_kwargs = step.args

        # action_kwargs有可能有:结构有可能是一个str、dict{}  有可能没有:结构是个空字典{}

        if isinstance(action_kwargs, str):
            action_kwargs = asdict(state.active_system_task)[action_kwargs.split(".")[1]]

        return ActionCall(
            action_name=action_name,
            action_kwargs=action_kwargs
        )
