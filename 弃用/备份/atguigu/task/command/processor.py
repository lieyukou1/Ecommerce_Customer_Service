from atguigu.domain.contexts import TaskContext, InterruptedSystemContext, ResumedSystemContext, StartedSystemContext, \
    CanceledSystemContext
from atguigu.domain.state import DialogueState
from atguigu.task.command.models import Command, StartFlowCommand, SetSlotsCommand, ResumeFlowCommand, \
    CancelFlowCommand
from atguigu.task.flow.flows import FlowList


class CommandProcessor:
    """

    """

    def run(self,
            state: DialogueState,
            flow_list: FlowList,
            commands: list[Command]) -> None:
        """

        """
        for command in commands:
            self._apply(state, command, flow_list)

    def _apply(self,
               state: DialogueState,
               command: Command,
               flow_list: FlowList):
        """

        """
        if isinstance(command, StartFlowCommand):
            self._handle_start_flow(state, command, flow_list)

        elif isinstance(command, SetSlotsCommand):
            self._handle_set_slots(state, command)

        elif isinstance(command, ResumeFlowCommand):
            self._handle_resume_flow(state, command, flow_list)

        elif isinstance(command, CancelFlowCommand):
            self._handle_cancel_flow(state, flow_list)

        else:
            pass

    def _handle_set_slots(self,
                          state: DialogueState,
                          command: SetSlotsCommand):
        """

        """
        if state.active_task is not None:
            state.set_slots(slots=command.slots)

    def _handle_start_flow(self,
                           state: DialogueState,
                           command: StartFlowCommand,
                           flow_list: FlowList):
        """
        开启业务任务：1)
        业务任务的流程ID: command.flow
        业务任务的流程名字：_readable_flow_name()
        """

        # 0.0系统流程情况
        state.end_active_system_task()
        # 0.1判断现在开启的流程是否为系统流程
        if command.flow.startswith('system'):
            raise ValueError(f"不能开启系统流程流程ID: {command.flow}")

        # 0.2判断流程是否存在
        if not flow_list.get_flow_by_id(flow_id=command.flow):
            raise ValueError(f"开启的流程ID: {command.flow} 对应的流程不存在")

        target_flow = flow_list.get_flow_by_id(flow_id=command.flow)

        # 1.开启一个新业务之前，先判断当前有没有业务任务
        active_task = state.active_task

        # 1.1已有业务任务
        if active_task is not None:
            # 1.1.1开启的业务任务当前正在执行
            if active_task.flow_id == command.flow:
                return  # 不再重复开启

            # 1.1.2开启的业务任务并非当前正在执行的任务
            # 1.1.2.1中断其他任务
            state.interrupt_active_task()
            interrupted_flow_id = active_task.flow_id
            interrupted_flow_name = self._readable_flow_name(active_task.flow_id,
                                                             flow_list)

            # 1.1.2.2检查任务自己是否在栈中
            # 1.1.2.2.1栈中无任务自己，新开业务认为并引出开场白
            if not state.resume_task(flow_id=command.flow):
                started_flow_id = command.flow
                started_flow_name = self._readable_flow_name(command.flow, flow_list)

                state.start_active_task(
                    task_context=TaskContext(
                        flow_id=target_flow.id,
                        step_id=target_flow.start_step().id
                    )
                )

            # 1.1.2.2.2栈中有任务自己，不需要重复开启任务，引出中断开场白
            else:

                started_flow_id = command.flow
                started_flow_name = self._readable_flow_name(command.flow, flow_list)

            # 1.1.2.3引出中断信息开场白
            self._activate_interrupted_system_task(state,
                                                   flow_list,
                                                   interrupted_flow_id=interrupted_flow_id,
                                                   interrupted_flow_name=interrupted_flow_name,
                                                   started_flow_id=started_flow_id,
                                                   started_flow_name=started_flow_name
                                                   )
            return

        # 1.2当前没有业务任务（活跃）
        # 栈中有任务自己，不用重复开启任务
        resumed = state.resume_task(flow_id=command.flow)
        if resumed:
            self._activate_resumed_system_flow(
                state,
                flow_list,
                resumed_flow_id=command.flow,
                resumed_flow_name=self._readable_flow_name(command.flow, flow_list)
            )
            return

        # 栈中无任务自己，开启任务，引出开场白
        state.start_active_task(
            task_context=TaskContext(
                flow_id=target_flow.id,
                step_id=target_flow.start_step().id
            )
        )

        self._activate_start_system_task(state,
                                         flow_list,
                                         start_flow_id=command.flow,
                                         start_flow_name=self._readable_flow_name(command.flow, flow_list))

    @staticmethod
    def _readable_flow_name(flow_id: str, flow_list: FlowList) -> str:
        """

        """
        flow = flow_list.get_flow_by_id(flow_id=flow_id)

        return flow.name if flow.name else flow_id

    @staticmethod
    def _activate_interrupted_system_task(state: DialogueState,
                                          flow_list: FlowList,
                                          *,
                                          interrupted_flow_id: str,
                                          interrupted_flow_name: str,
                                          started_flow_id: str,
                                          started_flow_name: str):
        flow = flow_list.get_flow_by_id("system_task_interrupted")
        state.start_active_system_task(
            InterruptedSystemContext(
                flow_id=flow.id,
                step_id=flow.start_step().id,
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,
                started_flow_id=started_flow_id,
                started_flow_name=started_flow_name
            )
        )

    @staticmethod
    def _activate_resumed_system_flow(state: DialogueState,
                                      flow_list: FlowList,
                                      resumed_flow_id: str,
                                      resumed_flow_name: str):
        """

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
    def _activate_start_system_task(state: DialogueState,
                                    flow_list: FlowList,
                                    start_flow_id: str,
                                    start_flow_name: str):
        """

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
    def _activate_cancel_system_flow(state: DialogueState,
                                     flow_list: FlowList,
                                     cancel_flow_id: str,
                                     cancel_flow_name: str):
        """

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

    def _handle_resume_flow(self,
                            state: DialogueState,
                            command: ResumeFlowCommand,
                            flow_list: FlowList):
        """

        """
        # ===== 第一步:确定要恢复哪个流程 =====
        if command.flow is not None:
            # 用户是否指定恢复
            target_flow = flow_list.get_flow_by_id(command.flow)
            if not target_flow:
                raise ValueError(f"Unknown flow '{command.flow}'.")
            target_flow_id = target_flow.id
            target_flow_name = target_flow.name
        else:
            # 不指定恢复，默认从栈顶弹出
            if not state.paused_tasks:
                return

            resumed = state.paused_tasks[-1]
            target_flow_id = resumed.flow_id
            target_flow_name = self._readable_flow_name(target_flow_id, flow_list)

        # ===== 第二步:按"当前有没有活跃任务"恢复 =====
        active_task = state.active_task

        if active_task:

            # 判断恢复的任务流程ID是否等于当前正在执行的业务任务流程ID
            if active_task.flow_id == target_flow_id:
                return

            state.interrupt_active_task()
            interrupted_flow_id = active_task.flow_id
            interrupted_flow_name = self._readable_flow_name(active_task.flow_id, flow_list)

            if not state.resume_task(flow_id=target_flow_id):
                state.resume_task()
                return

            self._activate_resumed_system_flow(state,
                                               flow_list,
                                               resumed_flow_id=target_flow_id,
                                               resumed_flow_name=target_flow_name, )

        else:
            if not state.resume_task(flow_id=command.flow):
                return

            resumed = state.active_task
            self._activate_resumed_system_flow(state,
                                               flow_list,
                                               resumed_flow_id=resumed.flow_id,
                                               resumed_flow_name=self._readable_flow_name(resumed.flow_id, flow_list))

    def _handle_cancel_flow(self,
                            state: DialogueState,
                            flow_list: FlowList):
        """

        """
        # 1. 激活系统的取消流程
        task = state.active_task
        if task is None and state.paused_tasks:
            task = state.paused_tasks[-1]

        if task is None:
            return

        flow = flow_list.get_flow_by_id(task.flow_id)

        self._activate_cancel_system_flow(state,
                                          flow_list,
                                          cancel_flow_id=flow.id,
                                          cancel_flow_name=self._readable_flow_name(task.flow_id, flow_list))

        state.end_active_task()
        state.clear_paused_tasks()
        state.clear_focused_object()
