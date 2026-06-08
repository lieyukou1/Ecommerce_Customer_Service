from typing import Dict

from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.turn_plan import TurnPlan, ClarifyReason, TurnPlanValidationResult
from atguigu.task.command.models import StartFlowCommand, ResumeFlowCommand, CancelFlowCommand, SetSlotsCommand
from atguigu.task.flow.flows import FlowList


class TurnPlanValidator:

    def validate(self,
                 state: DialogueState,
                 *,
                 turn_plan: TurnPlan,
                 flows: FlowList,
                 intents: Dict[str, KnowledgeIntent]):
        """
        校验 turn_plan
        """
        # 1.获取活跃轨道列表
        active_tracks: list[str] = self._get_active_tracks(turn_plan)

        # 2.判断是否存在
        if not active_tracks:
            return self._reject(reason=ClarifyReason.MISSING_TRACK)

        # 3.判断是否存在多个
        if len(active_tracks) > 1:
            return self._reject(reason=ClarifyReason.MULTIPLE_TRACKS)

        # 4.判断轨道究竟是哪个
        if active_tracks[0] == 'task':
            return self._validate_task(turn_plan, flows=flows)

        if active_tracks[0] == 'knowledge':
            return self._validate_knowledge(turn_plan, state=state, intents=intents)

        return TurnPlanValidationResult(valid=True)

    @staticmethod
    def _get_active_tracks(turn_plan: TurnPlan) -> list[str]:
        """

        """
        active_tracks = []

        if turn_plan.task is not None:
            active_tracks.append('task')

        if turn_plan.knowledge is not None:
            active_tracks.append('knowledge')

        if turn_plan.chitchat is not None:
            active_tracks.append('chitchat')

        return active_tracks

    def _reject(self, reason: ClarifyReason) -> TurnPlanValidationResult:
        """

        """
        return TurnPlanValidationResult(
            valid=False,
            reason=reason,
        )

    def _validate_task(self, turn_plan: TurnPlan, flows: FlowList) -> TurnPlanValidationResult:
        """

        """
        task = turn_plan.task
        # 第一重:commands 不能为空
        if not task or not task.commands:
            return self._reject(reason=ClarifyReason.MISSING_TASK_COMMANDS)

        # 第二重:每个 command 都得是认识的类型
        allowed = (StartFlowCommand, ResumeFlowCommand, CancelFlowCommand, SetSlotsCommand)
        for command in task.commands:
            if type(command) not in allowed:
                return self._reject(reason=ClarifyReason.INVALID_TASK_COMMANDS)

        # 第三重:不能一次开多个start流程
        start_commands = []
        for command in task.commands:
            if isinstance(command, StartFlowCommand):
                start_commands.append(command)
        if len(start_commands) > 1:
            return self._reject(reason=ClarifyReason.MULTIPLE_TASK_FLOWS)

        # 第四重:要开的流程必须真实存在
        if start_commands:
            start_flow_id = start_commands[0].flow
            if start_flow_id.startswith("system"):
                return self._reject(reason=ClarifyReason.INVALID_TASK_COMMANDS)

            flow = flows.get_flow_by_id(start_flow_id)

            if not flow:
                return self._reject(reason=ClarifyReason.UNKNOWN_TASK_FLOW)

        return TurnPlanValidationResult(valid=True)

    def _validate_knowledge(self,
                            turn_plan: TurnPlan,
                            state: DialogueState,
                            intents: Dict[str, KnowledgeIntent]
                            ) -> TurnPlanValidationResult:
        """

        """
        knowledge_plan = turn_plan.knowledge
        if knowledge_plan is None or not knowledge_plan.intents:
            return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)

        focused_object = state.focused_object
        for intent in knowledge_plan.intents:
            intent_meta = intents.get(intent)
            if intent_meta is None:
                return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)
            required_object = intent_meta.requires_object
            if required_object is not None:
                if focused_object is None or focused_object.type != required_object:
                    return self._reject(ClarifyReason.MISSING_FOCUSED_OBJECT)

        return TurnPlanValidationResult(valid=True)
