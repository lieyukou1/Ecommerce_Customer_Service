from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.engine.state_decision import StateDecisionEngine
from atguigu.task.command.models import Command
from atguigu.task.handler import TaskHandler


class TaskCommandExecutor:
    def __init__(
        self,
        *,
        task_handler: TaskHandler,
        state_decision: StateDecisionEngine,
    ) -> None:
        """
        功能：构造 task 执行包装器，在真正执行业务命令前后补齐状态迁移。

        输入：
        - task_handler: 负责执行业务 task command 的核心处理器。
        - state_decision: 负责 route decision 和 task outcome 回写。

        输出：
        - 无返回值；初始化执行包装器依赖。

        调用情况：
        - 由 `build_track_execution_runtime()` 创建，供文本轨和对象轨共用。

        副作用：
        - 无；只保存依赖引用。
        """
        self.task_handler = task_handler
        self.state_decision = state_decision

    async def execute(
        self,
        dialogue_state: DialogueState,
        *,
        commands: list[Command],
        route_event: str,
        route_reason: str | None,
        source_event: str,
        default_reason: str | None,
        semantic_kind: str | None = None,
    ) -> list[BotMessage]:
        """
        功能：执行 task 命令，并在前后统一记录路由决策和任务结果状态。

        输入：
        - dialogue_state: 当前运行时状态。
        - commands: 要交给 task handler 的命令列表。
        - route_event: 本轮进入 task 轨的事件名。
        - route_reason: 本轮进入 task 轨的原因说明。
        - source_event: 生成 task outcome 时使用的事件前缀。
        - default_reason: task 完成后默认回写的原因说明。
        - semantic_kind: 当前轮次的语义分类。

        输出：
        - list[BotMessage]: task handler 返回的机器人回复。

        调用情况：
        - 由 `TextTurnHandler` 和 `ObjectTurnHandler` 调用。

        副作用：
        - 会修改 route、task outcome 和 conversation state，并可能由 task handler 改写 active_task 等运行时状态。
        """
        # 在真正执行业务命令前，先把这轮 route 决策写入状态机。
        self.state_decision.begin_task_execution(
            dialogue_state,
            route_event=route_event,
            route_reason=route_reason,
            semantic_kind=semantic_kind,
        )
        # 这里才是 task 业务命令的真实执行点。
        messages = await self.task_handler.handle(
            state=dialogue_state,
            commands=commands,
        )
        # task handler 改完状态后，再根据最新状态补一笔 task outcome。
        self.state_decision.finalize_task_execution(
            dialogue_state,
            commands=commands,
            source_event=source_event,
            default_reason=default_reason,
            semantic_kind=semantic_kind,
        )
        return messages
