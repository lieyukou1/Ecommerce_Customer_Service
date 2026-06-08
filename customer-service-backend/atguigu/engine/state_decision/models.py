from dataclasses import dataclass

from atguigu.plan.turn_plan import TurnPlan
from atguigu.engine.state_decision.semantic_kind import SemanticKind


@dataclass(slots=True)
class ContextDecision:
    kind: str
    event: str
    reason: str | None = None
    semantic_kind: str | None = None


@dataclass(slots=True)
class TaskTransitionOutcome:
    kind: str
    event: str
    reason: str | None = None
    semantic_kind: str | None = None


@dataclass(slots=True)
class TextTurnContext:
    turn_plan: TurnPlan
    semantic_kind: SemanticKind
    decision: ContextDecision
