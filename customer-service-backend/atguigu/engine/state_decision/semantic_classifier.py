from atguigu.domain.state import DialogueState
from atguigu.engine.state_decision.semantic_kind import SemanticKind
from atguigu.engine.state_decision.task_flow_locator import TaskFlowLocator
from atguigu.plan.turn_plan import TurnPlan
from atguigu.task.flow.semantics import is_read_only_flow


class TurnSemanticClassifier:
    def __init__(self) -> None:
        """
        功能：构造文本轮次语义分类器。

        输入：
        - 无。

        输出：
        - 无返回值；初始化 flow 定位器依赖。

        调用情况：
        - 由 `StateDecisionEngine.__init__()` 创建。

        副作用：
        - 无。
        """
        self.task_flow_locator = TaskFlowLocator()

    def classify(
        self,
        dialogue_state: DialogueState,
        turn_plan: TurnPlan,
    ) -> SemanticKind:
        """
        功能：把 TurnPlan 归类成运行时需要的语义类型。

        输入：
        - dialogue_state: 当前运行时状态。
        - turn_plan: 协议闸门通过后的轮次计划。

        输出：
        - SemanticKind: 只读查询、业务任务、运行时控制或社交/澄清类型。

        调用情况：
        - 由 `StateDecisionEngine.build_text_context()` 调用。

        副作用：
        - 无。
        """
        active_track = turn_plan.active_track()

        if active_track is None:
            return SemanticKind.SOCIAL_OR_CLARIFY
        if turn_plan.directive is not None:
            return SemanticKind.RUNTIME_CONTROL
        if turn_plan.knowledge is not None:
            return SemanticKind.READ_ONLY_QUERY

        if turn_plan.task is not None:
            # task 轨还要继续区分“只读查询型 flow”还是“真实业务办理型 flow”。
            flow_id = self.task_flow_locator.resolve_flow_id(
                dialogue_state,
                turn_plan.task.commands,
            )
            if is_read_only_flow(flow_id):
                return SemanticKind.READ_ONLY_QUERY
            return SemanticKind.BUSINESS_TASK

        return SemanticKind.SOCIAL_OR_CLARIFY
