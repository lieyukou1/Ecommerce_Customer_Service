from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.action.runner import ActionRunner
from atguigu.task.command.models import Command
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.flow.executor import FlowExecutor
from atguigu.task.flow.flows import FlowList


class TaskHandler:

    def __init__(self, flows: FlowList,
                 processor: CommandProcessor,
                 action_runner: ActionRunner,
                 flow_executor: FlowExecutor,):
        self.flows = flows
        self.processor = processor
        self.action_runner = action_runner
        self.flow_executor = flow_executor

    async def handle(self,
               state: DialogueState,
               *,
               commands: list[Command], ) -> list[BotMessage]:
        """

        """
        # 1.利用processor处理command
        self.processor.run(state=state, flow_list=self.flows, commands=commands)

        # 2.推进流程Executor
        messages = await self.flow_executor.run_task(state, self.flows, self.action_runner)

        # 3.返回流程执行器得到的消息
        return messages
