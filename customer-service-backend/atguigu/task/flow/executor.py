from dataclasses import asdict

from atguigu.domain.contexts import CollectedSystemContext
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.base import ActionResult
from atguigu.task.action.runner import ActionCall, ActionRunner
from atguigu.task.flow.flows import FlowList
from atguigu.task.flow.links import ConditionalLink, FallbackLink, FlowStepLink, StaticLink
from atguigu.task.flow.steps import ActionFlowStep, CollectedFlowStep, EndFlowStep, FlowStep, StartedFlowStep


class FlowExecutor:
    """
    功能：推进 YAML 定义的业务 flow 与系统 flow，直到需要再次监听用户输入。
    """

    async def run_task(
        self,
        state: DialogueState,
        flows: FlowList,
        action_runner: ActionRunner,
    ):
        """
        功能：持续推进当前活跃 flow，直到遇到 `action_listen`。

        输入：
        - state: 当前运行时状态。
        - flows: 当前可用 flow 列表。
        - action_runner: action step 的执行器。

        输出：
        - list[BotMessage]: flow 推进过程中累计产生的机器人消息。

        调用情况：
        - `TaskHandler.handle()`

        副作用：
        - 会推进 step_id、写入槽位、启动系统收集任务，或结束当前任务上下文。
        """
        messages: list[BotMessage] = []

        while True:
            # 一直推进 flow，直到遇到一个需要真实执行的 action。
            action_call: ActionCall = self._advance_until_action(state, flows)
            if action_call.action_name == "action_listen":
                break

            # action 自己不直接改 state；统一由执行器把 slot_updates 写回当前任务。
            action_result: ActionResult = await action_runner.run(action_call, state)
            state.set_slots(action_result.slot_updates)
            messages.extend(action_result.messages)

        return messages

    def _advance_until_action(
        self,
        state: DialogueState,
        flows: FlowList,
    ) -> ActionCall:
        """
        功能：沿当前 active task / active system task 连续推进 step，直到产出一个 action call。

        输入：
        - state: 当前运行时状态。
        - flows: 当前可用 flow 列表。

        输出：
        - ActionCall: 下一步要执行的动作；若无活跃任务则返回 `action_listen`。

        调用情况：
        - `run_task()`

        副作用：
        - 会推进当前 step_id，并可能创建系统收集任务或结束任务。
        """
        while True:
            current_active_task = state.current_active_task()
            if current_active_task is None:
                return ActionCall(action_name="action_listen")

            flow = flows.get_flow_by_id(current_active_task.flow_id)
            step = flow.get_step_by_id(current_active_task.step_id)
            action_call: ActionCall | None = self._run_step(state, step, flows)
            if action_call is not None:
                return action_call

    def _run_step(
        self,
        state: DialogueState,
        step: FlowStep,
        flows: FlowList,
    ) -> ActionCall | None:
        """
        功能：按 step 类型执行当前 step。

        输入：
        - state: 当前运行时状态。
        - step: 当前要运行的 step。
        - flows: 当前可用 flow 列表。

        输出：
        - ActionCall | None: action step 时返回动作调用；纯推进 step 时返回 None。

        调用情况：
        - `_advance_until_action()`

        副作用：
        - 取决于具体 step 类型，可能推进 step、补槽、创建系统任务或结束任务。
        """
        if isinstance(step, StartedFlowStep):
            return self._run_start_step(step, state)
        if isinstance(step, CollectedFlowStep):
            return self._run_collect_slots_step(step, state, flows)
        if isinstance(step, EndFlowStep):
            return self._run_end_step(state)
        if isinstance(step, ActionFlowStep):
            return self._run_action_step(step, state)
        return None

    def _run_start_step(
        self,
        step: StartedFlowStep,
        state: DialogueState,
    ) -> None:
        """
        功能：执行 start step，仅负责推进到下一步。

        输入：
        - step: 当前 start step。
        - state: 当前运行时状态。

        输出：
        - None。

        调用情况：
        - `_run_step()` 在 `StartedFlowStep` 分支调用。

        副作用：
        - 会推进当前任务的 `step_id`。
        """
        self._advance_next_step(state, step)
        return None

    def _advance_next_step(
        self,
        state: DialogueState,
        step: FlowStep,
    ):
        """
        功能：根据当前 step 的 next links 计算并写入下一个 step_id。

        输入：
        - state: 当前运行时状态。
        - step: 当前 step。

        输出：
        - 无返回值。

        调用情况：
        - 多个 step 执行分支都会复用。

        副作用：
        - 会修改当前 active task 或 active system task 的 `step_id`。
        """
        next_step_id = self._select_next_step(step, state)
        state.current_active_task().step_id = next_step_id

    def _select_next_step(
        self,
        step: FlowStep,
        state: DialogueState,
    ) -> str:
        """
        功能：根据静态边、条件边和 fallback 边选择下一个 step。

        输入：
        - step: 当前 step。
        - state: 当前运行时状态。

        输出：
        - str: 下一个 step_id。

        调用情况：
        - `_advance_next_step()`

        副作用：
        - 无。
        """
        links: list[FlowStepLink] = step.next
        for link in links:
            if isinstance(link, StaticLink):
                return link.target
            if isinstance(link, ConditionalLink):
                if self._eval_condition(link.condition, state):
                    return link.target
            if isinstance(link, FallbackLink):
                return link.target

    def _eval_condition(
        self,
        condition: str,
        state: DialogueState,
    ) -> bool:
        """
        功能：在当前任务上下文中计算 flow 条件表达式。

        输入：
        - condition: YAML step 中定义的条件表达式。
        - state: 当前运行时状态。

        输出：
        - bool: 条件表达式的计算结果。

        调用情况：
        - `_select_next_step()`
        - 收集槽位校验逻辑

        副作用：
        - 无；仅做条件判断。
        """
        data = {
            "slots": state.active_task.slots,
            "context": asdict(state.current_active_task()),
        }
        return bool(eval(condition, {}, data))

    def _run_collect_slots_step(
        self,
        step: CollectedFlowStep,
        state: DialogueState,
        flows: FlowList,
    ) -> ActionCall | None:
        """
        功能：执行 collect step，处理自动补槽、槽位校验和系统追问。

        输入：
        - step: 当前 collect step。
        - state: 当前运行时状态。
        - flows: 当前可用 flow 列表。

        输出：
        - ActionCall | None: 需要立刻回复校验失败消息时返回 action_response，否则返回 None。

        调用情况：
        - `_run_step()` 在 `CollectedFlowStep` 分支调用。

        副作用：
        - 可能自动补槽、移除无效槽位、创建 `system_collect_information` 系统任务，或推进到下一步。
        """
        # 先尝试利用 focused object 自动补当前 collect step 所需槽位。
        self._try_fill_slot_from_focused_object(state, step)

        if state.active_task.slots.get(step.slot_name):
            # 槽位已存在时，若定义了 validate，则继续做条件校验。
            if step.validate:
                if self._eval_condition(condition=step.validate.condition, state=state):
                    self._advance_next_step(state, step)
                    return None

                # 校验失败时先删除错误槽位，再给出失败提示，保持任务继续停在 collect 位点。
                state.remove_slot(slot_name=step.slot_name)
                if step.validate.failure_response:
                    return ActionCall(
                        action_name="action_response",
                        action_kwargs=asdict(step.validate.failure_response),
                    )
                return ActionCall(
                    action_name="action_response",
                    action_kwargs={"text": "您填写的信息有误，请您重新再填。"},
                )

            # 没有校验规则时，说明当前槽位已满足要求，可以直接推进。
            self._advance_next_step(state, step)
            return None

        # 槽位还没就位时，切到系统收集 flow，让系统先问用户这一项缺失信息。
        state.start_active_system_task(
            CollectedSystemContext(
                flow_id="system_collect_information",
                step_id=flows.get_flow_by_id("system_collect_information").start_step().id,
                slot_name=step.slot_name,
                response=asdict(step.response),
            )
        )
        return None

    def _try_fill_slot_from_focused_object(
        self,
        state: DialogueState,
        step: CollectedFlowStep,
    ):
        """
        功能：尝试从 focused object 自动填充当前 collect step 需要的槽位。

        输入：
        - state: 当前运行时状态。
        - step: 当前 collect step。

        输出：
        - 无返回值。

        调用情况：
        - `_run_collect_slots_step()`

        副作用：
        - 命中对象字段映射时，会直接写入 `active_task.slots`。
        """
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

    def _run_end_step(
        self,
        state: DialogueState,
    ) -> None:
        """
        功能：执行 end step，结束当前系统任务或业务任务。

        输入：
        - state: 当前运行时状态。

        输出：
        - None。

        调用情况：
        - `_run_step()` 在 `EndFlowStep` 分支调用。

        副作用：
        - 会结束 `active_system_task` 或 `active_task`。
        """
        if state.active_system_task:
            state.end_active_system_task()
            return None
        if state.active_task:
            state.end_active_task()
            return None

    def _run_action_step(
        self,
        step: ActionFlowStep,
        state: DialogueState,
    ) -> ActionCall:
        """
        功能：执行 action step，先推进 step，再返回待执行的动作调用。

        输入：
        - step: 当前 action step。
        - state: 当前运行时状态。

        输出：
        - ActionCall: 交给 action runner 的动作调用对象。

        调用情况：
        - `_run_step()` 在 `ActionFlowStep` 分支调用。

        副作用：
        - 会先推进当前 step_id。
        """
        self._advance_next_step(state, step)
        return self._build_action_call(state, step)

    def _build_action_call(
        self,
        state: DialogueState,
        step: ActionFlowStep,
    ) -> ActionCall:
        """
        功能：把 action step 转成运行时可执行的 ActionCall。

        输入：
        - state: 当前运行时状态。
        - step: 当前 action step。

        输出：
        - ActionCall: 具体动作名和动作参数。

        调用情况：
        - `_run_action_step()`

        副作用：
        - 无；仅构造动作调用对象。
        """
        action_name = step.action
        action_kwargs = step.args

        # 当 args 是字符串引用时，表示应从 active_system_task 上取对应字段作为动作参数。
        if isinstance(action_kwargs, str):
            action_kwargs = asdict(state.active_system_task)[action_kwargs.split(".")[1]]

        return ActionCall(
            action_name=action_name,
            action_kwargs=action_kwargs,
        )
