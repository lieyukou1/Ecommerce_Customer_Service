from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.runner import ActionRunner
from atguigu.task.command.models import Command
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.flow.executor import FlowExecutor
from atguigu.task.flow.flows import FlowList


class TaskHandler:
    def __init__(
        self,
        flows: FlowList,
        processor: CommandProcessor,
        action_runner: ActionRunner,
        flow_executor: FlowExecutor,
    ):
        """
        功能：构造 task 执行总入口，连接命令处理器、动作执行器和 flow 推进器。

        输入：
        - flows: 当前可用的全部 flow 配置。
        - processor: 负责把 command 写入状态的命令处理器。
        - action_runner: 负责执行 action step 的运行器。
        - flow_executor: 负责推进 flow step 的执行器。

        输出：
        - 无返回值；初始化 task handler 依赖。

        调用情况：
        - 由装配层创建，供 `TaskCommandExecutor.execute()` 调用。

        副作用：
        - 无；只保存依赖引用。
        """
        self.flows = flows
        self.processor = processor
        self.action_runner = action_runner
        self.flow_executor = flow_executor

    async def handle(
        self,
        state: DialogueState,
        *,
        commands: list[Command],
    ) -> list[BotMessage]:
        """
        功能：执行一轮 task 命令，并推进 flow 直到下一个监听点。

        输入：
        - state: 当前住户的运行时状态。
        - commands: 本轮需要执行的 task 命令列表。

        输出：
        - list[BotMessage]: flow 推进过程中产生的机器人消息。

        调用情况：
        - 由 `TaskCommandExecutor.execute()` 调用。

        副作用：
        - 会修改 active_task、active_system_task、slots、focused_object 等 task 相关状态。
        """
        # 先把 planner 产出的命令翻译成状态变化，例如启动 flow、补槽、恢复或取消任务。
        self.processor.run(state=state, flow_list=self.flows, commands=commands)
        # 再沿当前 active task / active system task 推进 flow，直到需要再次监听用户输入。
        messages = await self.flow_executor.run_task(state, self.flows, self.action_runner)
        return messages
