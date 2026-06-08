from typing import Dict

from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.turn_plan import ClarifyReason, TurnPlan, TurnPlanTrack, TurnPlanValidationResult
from atguigu.task.command.models import CancelFlowCommand, ResumeFlowCommand, SetSlotsCommand, StartFlowCommand
from atguigu.task.flow.flows import FlowList

ALLOWED_TASK_COMMAND_TYPES = (StartFlowCommand, ResumeFlowCommand, CancelFlowCommand, SetSlotsCommand)


class TurnPlanValidator:
    def validate(
        self,
        state: DialogueState,
        *,
        turn_plan: TurnPlan,
        flows: FlowList,
        intents: Dict[str, KnowledgeIntent],
    ) -> TurnPlanValidationResult:
        """
        功能：校验当前 TurnPlan 是否满足执行前的协议约束。

        输入：
        - state: 当前运行时状态。
        - turn_plan: 已归一化的 TurnPlan。
        - flows: 当前可用 flow 列表。
        - intents: 当前可用知识意图注册表。

        输出：
        - TurnPlanValidationResult: 校验通过或失败的结果对象。

        调用情况：
        - 由 `TurnProtocolGate.process()` 调用。

        副作用：
        - 无；只返回 accept/reject 结果。
        """
        active_tracks = turn_plan.active_tracks()
        if not active_tracks:
            return self._reject(ClarifyReason.MISSING_TRACK)
        if len(active_tracks) > 1:
            return self._reject(ClarifyReason.MULTIPLE_TRACKS)

        active_track = active_tracks[0]
        if active_track is TurnPlanTrack.DIRECTIVE:
            return self._validate_directive(turn_plan)
        if active_track is TurnPlanTrack.TASK:
            return self._validate_task(turn_plan, flows)
        if active_track is TurnPlanTrack.KNOWLEDGE:
            return self._validate_knowledge(turn_plan, state, intents)

        return TurnPlanValidationResult.accept()

    @staticmethod
    def _reject(reason: ClarifyReason | None) -> TurnPlanValidationResult:
        """
        功能：构造统一的协议拒绝结果。

        输入：
        - reason: 当前拒绝原因。

        输出：
        - TurnPlanValidationResult: 带澄清上下文的 reject 结果。

        调用情况：
        - 由各校验失败分支复用。

        副作用：
        - 无。
        """
        return TurnPlanValidationResult.reject(reason)

    def _validate_task(
        self,
        turn_plan: TurnPlan,
        flows: FlowList,
    ) -> TurnPlanValidationResult:
        """
        功能：校验 task 轨是否包含合法命令且指向存在的业务 flow。

        输入：
        - turn_plan: 当前轮次计划。
        - flows: 当前可用 flow 列表。

        输出：
        - TurnPlanValidationResult: task 轨的校验结果。

        调用情况：
        - 由 `validate()` 在 task 轨分支调用。

        副作用：
        - 无。
        """
        task = turn_plan.task
        if task is None or not task.commands:
            return self._reject(ClarifyReason.MISSING_TASK_COMMANDS)

        invalid_command = next(
            (command for command in task.commands if type(command) not in ALLOWED_TASK_COMMAND_TYPES),
            None,
        )
        if invalid_command is not None:
            return self._reject(ClarifyReason.INVALID_TASK_COMMANDS)

        start_commands = self._collect_start_commands(task.commands)
        if len(start_commands) > 1:
            return self._reject(ClarifyReason.MULTIPLE_TASK_FLOWS)
        if not start_commands:
            return TurnPlanValidationResult.accept()

        # start 命令只能指向已注册的业务 flow，不能直接启动 system flow。
        start_flow_id = start_commands[0].flow
        if start_flow_id.startswith("system"):
            return self._reject(ClarifyReason.INVALID_TASK_COMMANDS)

        flow = flows.get_flow_by_id(start_flow_id)
        if flow is None:
            return self._reject(ClarifyReason.UNKNOWN_TASK_FLOW)

        return TurnPlanValidationResult.accept()

    def _validate_directive(self, turn_plan: TurnPlan) -> TurnPlanValidationResult:
        """
        功能：校验 directive 轨是否是当前运行时协议支持的指令。

        输入：
        - turn_plan: 当前轮次计划。

        输出：
        - TurnPlanValidationResult: directive 轨的校验结果。

        调用情况：
        - 由 `validate()` 在 directive 轨分支调用。

        副作用：
        - 无。
        """
        directive = turn_plan.directive
        if directive is None or not directive.is_exit_runtime():
            return self._reject(ClarifyReason.INVALID_DIRECTIVE)
        return TurnPlanValidationResult.accept()

    def _validate_knowledge(
        self,
        turn_plan: TurnPlan,
        state: DialogueState,
        intents: Dict[str, KnowledgeIntent],
    ) -> TurnPlanValidationResult:
        """
        功能：校验 knowledge 轨的意图是否存在，并满足对象依赖。

        输入：
        - turn_plan: 当前轮次计划。
        - state: 当前运行时状态。
        - intents: 当前可用知识意图注册表。

        输出：
        - TurnPlanValidationResult: knowledge 轨的校验结果。

        调用情况：
        - 由 `validate()` 在 knowledge 轨分支调用。

        副作用：
        - 无。
        """
        knowledge_plan = turn_plan.knowledge
        if knowledge_plan is None or not knowledge_plan.intents:
            return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)

        focused_object = state.focused_object
        for intent in knowledge_plan.intents:
            intent_meta = intents.get(intent)
            if intent_meta is None:
                return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)
            if self._requires_missing_object(intent_meta.requires_object, focused_object):
                return self._reject(ClarifyReason.MISSING_FOCUSED_OBJECT)

        return TurnPlanValidationResult.accept()

    @staticmethod
    def _collect_start_commands(commands: list) -> list[StartFlowCommand]:
        """
        功能：从命令列表中筛出 StartFlowCommand。

        输入：
        - commands: 当前 task 命令列表。

        输出：
        - list[StartFlowCommand]: 所有 start 命令。

        调用情况：
        - 由 `_validate_task()` 调用。

        副作用：
        - 无。
        """
        return [command for command in commands if isinstance(command, StartFlowCommand)]

    @staticmethod
    def _requires_missing_object(
        required_object: str | None,
        focused_object,
    ) -> bool:
        """
        功能：判断知识意图要求的对象类型是否缺失。

        输入：
        - required_object: 意图要求的对象类型，可为空。
        - focused_object: 当前对话中的 focused object。

        输出：
        - bool: 缺少必需对象或对象类型不匹配时返回 True。

        调用情况：
        - 由 `_validate_knowledge()` 调用。

        副作用：
        - 无。
        """
        if required_object is None:
            return False
        return focused_object is None or focused_object.type != required_object
