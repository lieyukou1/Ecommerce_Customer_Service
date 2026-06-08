from atguigu.domain.contexts import (
    CanceledSystemContext,
    InterruptedSystemContext,
    ResumedSystemContext,
    StartedSystemContext,
    TaskContext,
)
from atguigu.domain.state import DialogueState
from atguigu.task.command.models import (
    CancelFlowCommand,
    Command,
    ResumeFlowCommand,
    SetSlotsCommand,
    StartFlowCommand,
)
from atguigu.task.flow.flows import FlowList


class CommandProcessor:
    """
    功能：把 planner 产出的 task command 翻译成 DialogueState 的即时状态修改。
    """

    def run(
        self,
        state: DialogueState,
        flow_list: FlowList,
        commands: list[Command],
    ) -> None:
        """
        功能：按顺序执行一组 task command。

        输入：
        - state: 当前运行时状态。
        - flow_list: 当前可用 flow 列表。
        - commands: 需要应用的命令列表。

        输出：
        - 无返回值；结果体现在 state 的即时变化上。

        调用情况：
        - `TaskHandler.handle()`

        副作用：
        - 会修改任务栈、系统任务、槽位、focused object 等运行时状态。
        """
        for command in commands:
            self._apply(state, command, flow_list)

    def _apply(
        self,
        state: DialogueState,
        command: Command,
        flow_list: FlowList,
    ):
        """
        功能：按命令类型把单个 command 分发到对应处理分支。

        输入：
        - state: 当前运行时状态。
        - command: 当前要执行的命令。
        - flow_list: 当前可用 flow 列表。

        输出：
        - 无返回值。

        调用情况：
        - `run()`

        副作用：
        - 会触发具体命令对应的状态修改。
        """
        if isinstance(command, StartFlowCommand):
            self._handle_start_flow(state, command, flow_list)
        elif isinstance(command, SetSlotsCommand):
            self._handle_set_slots(state, command)
        elif isinstance(command, ResumeFlowCommand):
            self._handle_resume_flow(state, command, flow_list)
        elif isinstance(command, CancelFlowCommand):
            self._handle_cancel_flow(state, flow_list)

    def _handle_set_slots(
        self,
        state: DialogueState,
        command: SetSlotsCommand,
    ):
        """
        功能：把命令中的槽位字典合并到当前 active_task。

        输入：
        - state: 当前运行时状态。
        - command: 当前 set_slots 命令。

        输出：
        - 无返回值。

        调用情况：
        - `_apply()` 在 `SetSlotsCommand` 分支调用。

        副作用：
        - 会修改 `active_task.slots`。
        """
        if state.active_task is not None:
            state.set_slots(slots=command.slots)

    def _handle_start_flow(
        self,
        state: DialogueState,
        command: StartFlowCommand,
        flow_list: FlowList,
    ):
        """
        功能：启动一个业务 flow，并处理它和当前任务栈的关系。

        输入：
        - state: 当前运行时状态。
        - command: 要启动的 flow 命令。
        - flow_list: 当前可用 flow 列表。

        输出：
        - 无返回值。

        调用情况：
        - `_apply()` 在 `StartFlowCommand` 分支调用。

        副作用：
        - 可能结束系统任务、打断当前任务、恢复旧任务、启动新任务，并激活对应系统提示流。
        """
        # 启动业务 flow 前，先结束当前系统提示流，避免旧系统提示残留。
        state.end_active_system_task()

        if command.flow.startswith("system"):
            raise ValueError(f"不能启动系统流程 flow_id: {command.flow}")

        target_flow = flow_list.get_flow_by_id(flow_id=command.flow)
        if not target_flow:
            raise ValueError(f"启动的 flow_id: {command.flow} 对应流程不存在")

        active_task = state.active_task
        if active_task is not None:
            # 已经就在执行同一个 flow 时，不再重复启动。
            if active_task.flow_id == command.flow:
                return

            # 切到新 flow 前，先把当前任务压入 paused_tasks。
            state.interrupt_active_task()
            interrupted_flow_id = active_task.flow_id
            interrupted_flow_name = self._readable_flow_name(active_task.flow_id, flow_list)

            # 若目标 flow 之前被挂起，则优先恢复；否则新建一条 active_task。
            if not state.resume_task(flow_id=command.flow):
                state.start_active_task(
                    task_context=TaskContext(
                        flow_id=target_flow.id,
                        step_id=target_flow.start_step().id,
                    )
                )

            # 无论是恢复还是新开，都给系统流一条“旧任务被打断，新任务接手”的过场提示。
            self._activate_interrupted_system_task(
                state,
                flow_list,
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,
                started_flow_id=command.flow,
                started_flow_name=self._readable_flow_name(command.flow, flow_list),
            )
            return

        # 当前没有 active_task 时，若目标 flow 早已在暂停栈里，直接恢复即可。
        resumed = state.resume_task(flow_id=command.flow)
        if resumed:
            self._activate_resumed_system_flow(
                state,
                flow_list,
                resumed_flow_id=command.flow,
                resumed_flow_name=self._readable_flow_name(command.flow, flow_list),
            )
            return

        # 真正的新启动只发生在“当前无 active_task，暂停栈里也没有目标 flow”的场景。
        state.start_active_task(
            task_context=TaskContext(
                flow_id=target_flow.id,
                step_id=target_flow.start_step().id,
            )
        )
        self._activate_start_system_task(
            state,
            flow_list,
            start_flow_id=command.flow,
            start_flow_name=self._readable_flow_name(command.flow, flow_list),
        )

    @staticmethod
    def _readable_flow_name(flow_id: str, flow_list: FlowList) -> str:
        """
        功能：把 flow_id 转成更适合展示给用户的 flow 名称。

        输入：
        - flow_id: 目标 flow 标识。
        - flow_list: 当前可用 flow 列表。

        输出：
        - str: flow.name 存在时返回名称，否则回退返回 flow_id。

        调用情况：
        - 多个任务切换与系统提示流构造函数复用。

        副作用：
        - 无。
        """
        flow = flow_list.get_flow_by_id(flow_id=flow_id)
        return flow.name if flow.name else flow_id

    @staticmethod
    def _activate_interrupted_system_task(
        state: DialogueState,
        flow_list: FlowList,
        *,
        interrupted_flow_id: str,
        interrupted_flow_name: str,
        started_flow_id: str,
        started_flow_name: str,
    ):
        """
        功能：激活“任务被打断并切到新任务”的系统提示流。

        输入：
        - state: 当前运行时状态。
        - flow_list: 当前可用 flow 列表。
        - interrupted_flow_id/interrupted_flow_name: 被打断的旧任务信息。
        - started_flow_id/started_flow_name: 新接手任务信息。

        输出：
        - 无返回值。

        调用情况：
        - `_handle_start_flow()`

        副作用：
        - 会设置 `active_system_task`。
        """
        flow = flow_list.get_flow_by_id("system_task_interrupted")
        state.start_active_system_task(
            InterruptedSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,
                started_flow_id=started_flow_id,
                started_flow_name=started_flow_name,
            )
        )

    @staticmethod
    def _activate_resumed_system_flow(
        state: DialogueState,
        flow_list: FlowList,
        resumed_flow_id: str,
        resumed_flow_name: str,
    ):
        """
        功能：激活“恢复旧任务”的系统提示流。

        输入：
        - state: 当前运行时状态。
        - flow_list: 当前可用 flow 列表。
        - resumed_flow_id/resumed_flow_name: 被恢复任务的信息。

        输出：
        - 无返回值。

        调用情况：
        - `_handle_start_flow()`
        - `_handle_resume_flow()`

        副作用：
        - 会设置 `active_system_task`。
        """
        flow = flow_list.get_flow_by_id("system_task_resumed")
        state.start_active_system_task(
            ResumedSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,
                resumed_flow_id=resumed_flow_id,
                resumed_flow_name=resumed_flow_name,
            )
        )

    @staticmethod
    def _activate_start_system_task(
        state: DialogueState,
        flow_list: FlowList,
        start_flow_id: str,
        start_flow_name: str,
    ):
        """
        功能：激活“新任务开始”的系统提示流。

        输入：
        - state: 当前运行时状态。
        - flow_list: 当前可用 flow 列表。
        - start_flow_id/start_flow_name: 新启动任务的信息。

        输出：
        - 无返回值。

        调用情况：
        - `_handle_start_flow()`

        副作用：
        - 会设置 `active_system_task`。
        """
        flow = flow_list.get_flow_by_id(flow_id="system_task_started")
        state.start_active_system_task(
            StartedSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,
                started_flow_id=start_flow_id,
                started_flow_name=start_flow_name,
            )
        )

    @staticmethod
    def _activate_cancel_system_flow(
        state: DialogueState,
        flow_list: FlowList,
        cancel_flow_id: str,
        cancel_flow_name: str,
    ):
        """
        功能：激活“任务取消”的系统提示流。

        输入：
        - state: 当前运行时状态。
        - flow_list: 当前可用 flow 列表。
        - cancel_flow_id/cancel_flow_name: 被取消任务的信息。

        输出：
        - 无返回值。

        调用情况：
        - `_handle_cancel_flow()`

        副作用：
        - 会设置 `active_system_task`。
        """
        flow = flow_list.get_flow_by_id("system_task_canceled")
        state.start_active_system_task(
            CanceledSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,
                canceled_flow_id=cancel_flow_id,
                canceled_flow_name=cancel_flow_name,
            )
        )

    def _handle_resume_flow(
        self,
        state: DialogueState,
        command: ResumeFlowCommand,
        flow_list: FlowList,
    ):
        """
        功能：恢复一个暂停任务，并处理它与当前 active_task 的冲突关系。

        输入：
        - state: 当前运行时状态。
        - command: resume_flow 命令。
        - flow_list: 当前可用 flow 列表。

        输出：
        - 无返回值。

        调用情况：
        - `_apply()` 在 `ResumeFlowCommand` 分支调用。

        副作用：
        - 可能打断当前任务、恢复暂停任务，并激活系统提示流。
        """
        # 先确定这次要恢复哪个 flow；未指定时默认恢复暂停栈顶。
        if command.flow is not None:
            target_flow = flow_list.get_flow_by_id(command.flow)
            if not target_flow:
                raise ValueError(f"Unknown flow '{command.flow}'.")
            target_flow_id = target_flow.id
            target_flow_name = target_flow.name
        else:
            if not state.paused_tasks:
                return
            resumed = state.paused_tasks[-1]
            target_flow_id = resumed.flow_id
            target_flow_name = self._readable_flow_name(target_flow_id, flow_list)

        active_task = state.active_task
        if active_task:
            # 当前已经在执行目标任务时，忽略这次恢复命令。
            if active_task.flow_id == target_flow_id:
                return

            # 当前有别的 active_task 时，先把它打断，再恢复目标任务。
            state.interrupt_active_task()
            if not state.resume_task(flow_id=target_flow_id):
                # 理论上目标 flow 应该就在暂停栈里；如果不在，回退恢复最近任务，避免状态悬空。
                state.resume_task()
                return

            self._activate_resumed_system_flow(
                state,
                flow_list,
                resumed_flow_id=target_flow_id,
                resumed_flow_name=target_flow_name,
            )
        else:
            if not state.resume_task(flow_id=command.flow):
                return

            resumed = state.active_task
            self._activate_resumed_system_flow(
                state,
                flow_list,
                resumed_flow_id=resumed.flow_id,
                resumed_flow_name=self._readable_flow_name(resumed.flow_id, flow_list),
            )

    def _handle_cancel_flow(
        self,
        state: DialogueState,
        flow_list: FlowList,
    ):
        """
        功能：取消当前任务上下文，并激活系统取消提示流。

        输入：
        - state: 当前运行时状态。
        - flow_list: 当前可用 flow 列表。

        输出：
        - 无返回值。

        调用情况：
        - `_apply()` 在 `CancelFlowCommand` 分支调用。

        副作用：
        - 会清理 `active_task`、`paused_tasks`、`focused_object`，并激活取消系统任务。
        """
        # 优先取消当前 active_task；若没有，再尝试取消最近一个暂停任务。
        task = state.active_task
        if task is None and state.paused_tasks:
            task = state.paused_tasks[-1]
        if task is None:
            return

        flow = flow_list.get_flow_by_id(task.flow_id)
        self._activate_cancel_system_flow(
            state,
            flow_list,
            cancel_flow_id=flow.id,
            cancel_flow_name=self._readable_flow_name(task.flow_id, flow_list),
        )

        # 取消是强收口操作：结束当前任务，清空被打断任务，并移除当前对象上下文。
        state.end_active_task()
        state.clear_paused_tasks()
        state.clear_focused_object()
