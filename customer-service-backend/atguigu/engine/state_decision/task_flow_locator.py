from atguigu.domain.state import DialogueState
from atguigu.task.command.models import Command, ResumeFlowCommand, StartFlowCommand


class TaskFlowLocator:
    def resolve_flow_id(
        self,
        dialogue_state: DialogueState,
        commands: list[Command],
    ) -> str | None:
        """
        功能：从 task 命令列表和当前状态里推断本轮实际指向的 flow_id。

        输入：
        - dialogue_state: 当前运行时状态。
        - commands: 当前轮次的 task 命令列表。

        输出：
        - str | None: 能定位到时返回目标 flow_id，否则返回 None。

        调用情况：
        - 由 `TurnSemanticClassifier.classify()` 调用，用于区分只读 flow 与业务 flow。

        副作用：
        - 无。
        """
        start_command = next((command for command in commands if isinstance(command, StartFlowCommand)), None)
        if start_command is not None:
            return start_command.flow

        resume_command = next((command for command in commands if isinstance(command, ResumeFlowCommand)), None)
        if resume_command is not None:
            if resume_command.flow is not None:
                return resume_command.flow
            if dialogue_state.active_task is not None:
                return dialogue_state.active_task.flow_id
            return None

        # 没有显式 start/resume 时，默认沿用当前 active task 的 flow。
        if dialogue_state.active_task is not None:
            return dialogue_state.active_task.flow_id

        return None
