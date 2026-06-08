from dataclasses import dataclass, field
from enum import Enum

from atguigu.task.command.models import Command


@dataclass(slots=True)
class TaskTurnPlan:
    commands: list[Command] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskTurnPlan":
        """
        功能：把字典形式的 task 计划还原成 TaskTurnPlan。

        输入：
        - data: 包含 `commands` 列表的字典。

        输出：
        - TaskTurnPlan: 反序列化后的 task 计划对象。

        调用情况：
        - 由 `TurnPlan.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(commands=[Command.from_dict(command) for command in data["commands"]])


@dataclass(slots=True)
class KnowledgeTurnPlan:
    intents: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeTurnPlan":
        """
        功能：把字典形式的 knowledge 计划还原成 KnowledgeTurnPlan。

        输入：
        - data: 包含 `intents` 列表的字典。

        输出：
        - KnowledgeTurnPlan: 反序列化后的知识计划对象。

        调用情况：
        - 由 `TurnPlan.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(intents=data["intents"])


@dataclass(slots=True)
class ChitchatTurnPlan:
    pass


class RuntimeDirectiveAction(str, Enum):
    EXIT_RUNTIME = "exit_runtime"


@dataclass(slots=True)
class RuntimeDirectiveTurnPlan:
    action: str

    @classmethod
    def from_dict(cls, data: dict) -> "RuntimeDirectiveTurnPlan":
        """
        功能：把字典形式的 runtime directive 计划还原成对象。

        输入：
        - data: 包含 `action` 字段的字典。

        输出：
        - RuntimeDirectiveTurnPlan: 反序列化后的运行时指令计划。

        调用情况：
        - 由 `TurnPlan.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(action=data["action"])

    def is_exit_runtime(self) -> bool:
        """
        功能：判断当前 runtime directive 是否为退出上下文指令。

        输入：
        - 无显式输入；依赖当前对象的 `action` 字段。

        输出：
        - bool: action 为 `exit_runtime` 时返回 True。

        调用情况：
        - 由 normalizer、validator、state decision 多处调用。

        副作用：
        - 无。
        """
        return self.action == RuntimeDirectiveAction.EXIT_RUNTIME.value


class TurnPlanTrack(str, Enum):
    TASK = "task"
    KNOWLEDGE = "knowledge"
    CHITCHAT = "chitchat"
    DIRECTIVE = "directive"


@dataclass(slots=True)
class TurnPlan:
    """
    功能：承载单轮对话的结构化规划结果。

    说明：
    - 当前协议要求一轮最终只落到一条主轨道。
    - 后续若要支持多意图并行，可在此基础上扩展。
    """

    task: TaskTurnPlan | None = None
    knowledge: KnowledgeTurnPlan | None = None
    chitchat: ChitchatTurnPlan | None = None
    directive: RuntimeDirectiveTurnPlan | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "TurnPlan":
        """
        功能：把模型输出的字典结构还原成 TurnPlan。

        输入：
        - data: 模型返回的 JSON 字典。

        输出：
        - TurnPlan: 结构化轮次计划对象。

        调用情况：
        - 由 `TurnPlanner._predict_from_inputs_prompt()` 调用。

        副作用：
        - 无。
        """
        return cls(
            task=TaskTurnPlan.from_dict(data["task"]) if data.get("task") is not None else None,
            knowledge=KnowledgeTurnPlan.from_dict(data["knowledge"]) if data.get("knowledge") is not None else None,
            chitchat=ChitchatTurnPlan() if data.get("chitchat") is not None else None,
            directive=RuntimeDirectiveTurnPlan.from_dict(data["directive"]) if data.get("directive") is not None else None,
        )

    def active_tracks(self) -> list[TurnPlanTrack]:
        """
        功能：列出当前 TurnPlan 中被激活的全部轨道。

        输入：
        - 无显式输入；依赖当前对象上的各轨字段。

        输出：
        - list[TurnPlanTrack]: 当前非空轨道集合。

        调用情况：
        - 由 validator、normalizer 等协议层组件调用。

        副作用：
        - 无。
        """
        tracks: list[TurnPlanTrack] = []
        if self.task is not None:
            tracks.append(TurnPlanTrack.TASK)
        if self.knowledge is not None:
            tracks.append(TurnPlanTrack.KNOWLEDGE)
        if self.chitchat is not None:
            tracks.append(TurnPlanTrack.CHITCHAT)
        if self.directive is not None:
            tracks.append(TurnPlanTrack.DIRECTIVE)
        return tracks

    def active_track(self) -> TurnPlanTrack | None:
        """
        功能：在只有单轨激活时，返回当前唯一有效轨道。

        输入：
        - 无显式输入；依赖 `active_tracks()` 的结果。

        输出：
        - TurnPlanTrack | None: 只有一条轨道时返回该轨；多轨或空轨时返回 None。

        调用情况：
        - 由语义分类器等组件调用。

        副作用：
        - 无。
        """
        tracks = self.active_tracks()
        if len(tracks) == 1:
            return tracks[0]
        return None


class ClarifyReason(str, Enum):
    MISSING_TRACK = "missing_track"
    MULTIPLE_TRACKS = "multiple_tracks"
    MISSING_TASK_COMMANDS = "missing_task_commands"
    MISSING_KNOWLEDGE_INTENT = "missing_knowledge_intent"
    MISSING_FOCUSED_OBJECT = "missing_focused_object"
    OBJECT_REQUIRES_INTENT = "object_requires_intent"
    INVALID_TASK_COMMANDS = "invalid_task_commands"
    MULTIPLE_TASK_FLOWS = "multiple_task_flows"
    UNKNOWN_TASK_FLOW = "unknown_task_flow"
    INVALID_DIRECTIVE = "invalid_directive"


class ClarifySource(str, Enum):
    VALIDATION = "validation"
    OBJECT = "object"


@dataclass(slots=True)
class ClarifyContext:
    source: ClarifySource
    reason: ClarifyReason | None = None

    @classmethod
    def for_validation(cls, reason: ClarifyReason | None) -> "ClarifyContext":
        """
        功能：构造“协议校验失败”来源的澄清上下文。

        输入：
        - reason: 导致校验失败的原因枚举。

        输出：
        - ClarifyContext: validation 来源的澄清上下文。

        调用情况：
        - 由 `TurnPlanValidationResult.reject()` 调用。

        副作用：
        - 无。
        """
        return cls(source=ClarifySource.VALIDATION, reason=reason)

    @classmethod
    def for_object_intent(cls) -> "ClarifyContext":
        """
        功能：构造“对象已选中但意图不明确”来源的澄清上下文。

        输入：
        - 无。

        输出：
        - ClarifyContext: object 来源的澄清上下文。

        调用情况：
        - 由 `ObjectTurnHandler` 调用。

        副作用：
        - 无。
        """
        return cls(
            source=ClarifySource.OBJECT,
            reason=ClarifyReason.OBJECT_REQUIRES_INTENT,
        )

    def is_object_intent(self) -> bool:
        """
        功能：判断当前澄清上下文是否来自对象意图不明确场景。

        输入：
        - 无显式输入；依赖 `source` 字段。

        输出：
        - bool: source 为 OBJECT 时返回 True。

        调用情况：
        - 由 clarify responder 等组件调用。

        副作用：
        - 无。
        """
        return self.source is ClarifySource.OBJECT


@dataclass(slots=True)
class TurnPlanValidationResult:
    valid: bool
    clarify_context: ClarifyContext | None = None

    @classmethod
    def accept(cls) -> "TurnPlanValidationResult":
        """
        功能：构造协议校验通过结果。

        输入：
        - 无。

        输出：
        - TurnPlanValidationResult: `valid=True` 的结果对象。

        调用情况：
        - 由 validator 内各通过分支调用。

        副作用：
        - 无。
        """
        return cls(valid=True)

    @classmethod
    def reject(cls, reason: ClarifyReason | None) -> "TurnPlanValidationResult":
        """
        功能：构造协议校验失败结果，并自动附带 validation 类型的澄清上下文。

        输入：
        - reason: 校验失败原因。

        输出：
        - TurnPlanValidationResult: `valid=False` 的结果对象。

        调用情况：
        - 由 validator 的拒绝分支调用。

        副作用：
        - 无。
        """
        return cls(valid=False, clarify_context=ClarifyContext.for_validation(reason))
