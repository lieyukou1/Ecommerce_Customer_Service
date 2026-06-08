from dataclasses import dataclass
from typing import Dict

from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.turn_plan import ClarifyContext, TurnPlan
from atguigu.plan.turn_plan_normalizer import TurnPlanNormalizer
from atguigu.plan.turn_validator import TurnPlanValidator
from atguigu.task.flow.flows import FlowList


@dataclass(slots=True)
class TurnProtocolGateResult:
    turn_plan: TurnPlan | None = None
    clarify_context: ClarifyContext | None = None

    @property
    def accepted(self) -> bool:
        """
        功能：标记当前 planner 结果是否通过协议闸门。

        输入：
        - 无显式输入；依赖当前结果对象上的 `turn_plan` 字段。

        输出：
        - bool: 存在合法 `turn_plan` 时返回 True，否则返回 False。

        调用情况：
        - 由 `TextTurnHandler.handle()` 读取，用于决定继续执行还是进入澄清分支。

        副作用：
        - 无。
        """
        return self.turn_plan is not None


class TurnProtocolGate:
    def __init__(
        self,
        *,
        turn_validator: TurnPlanValidator,
        turn_plan_normalizer: TurnPlanNormalizer | None = None,
    ) -> None:
        """
        功能：构造 planner 输出的协议闸门。

        输入：
        - turn_validator: 负责校验 TurnPlan 合法性的验证器。
        - turn_plan_normalizer: 负责把 planner 输出归一化成运行时协议的规范器，可为空。

        输出：
        - 无返回值；初始化协议闸门依赖。

        调用情况：
        - 由装配层创建，供 `TextTurnHandler` 复用。

        副作用：
        - 无；只保存依赖引用。
        """
        self.turn_validator = turn_validator
        self.turn_plan_normalizer = turn_plan_normalizer or TurnPlanNormalizer()

    def process(
        self,
        dialogue_state: DialogueState,
        *,
        turn_plan: TurnPlan,
        flows: FlowList,
        intents: Dict[str, KnowledgeIntent],
    ) -> TurnProtocolGateResult:
        """
        功能：对 planner 输出执行“归一化 -> 校验 -> 给出接受/拒绝结果”。

        输入：
        - dialogue_state: 当前运行时状态。
        - turn_plan: planner 刚产出的原始 TurnPlan。
        - flows: 当前可用 flow 列表。
        - intents: 当前可用知识意图注册表。

        输出：
        - TurnProtocolGateResult: 包含合法 turn_plan 或 clarify_context 的协议结果。

        调用情况：
        - 由 `TextTurnHandler.handle()` 调用。

        副作用：
        - 不直接修改状态；仅根据状态与协议规则判断是否放行。
        """
        # 先把 planner 输出收口成运行时真正识别的协议形态。
        normalized_turn_plan = self.turn_plan_normalizer.normalize(
            dialogue_state,
            turn_plan,
        )
        # 再检查 track、命令、意图和对象依赖是否满足执行条件。
        validated = self.turn_validator.validate(
            dialogue_state,
            turn_plan=normalized_turn_plan,
            flows=flows,
            intents=intents,
        )
        if not validated.valid:
            # 不放行时，只返回澄清上下文，让上层统一走 clarify 分支。
            return TurnProtocolGateResult(clarify_context=validated.clarify_context)

        return TurnProtocolGateResult(turn_plan=normalized_turn_plan)
