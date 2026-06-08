import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

from atguigu.domain.contexts import SystemContext, TaskContext
from atguigu.domain.messages import BotMessage, FocusedObject, UserMessage


class ConversationState(str, Enum):
    IDLE = "idle"
    FOCUSED_KNOWLEDGE = "focused_knowledge"
    CLARIFYING = "clarifying"
    ACTIVE_TASK = "active_task"
    CHITCHAT = "chitchat"
    TRANSITIONING = "transitioning"


@dataclass(slots=True)
class ConversationTransition:
    from_state: str
    to_state: str
    event: str
    reason: str | None = None
    at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """
        功能：把状态迁移记录序列化成字典。

        输入：
        - 无显式输入；依赖当前对象字段。

        输出：
        - Dict[str, Any]: 可持久化的状态迁移字典。

        调用情况：
        - 由 `DialogueState.to_dict()` 调用。

        副作用：
        - 无。
        """
        return {
            "from_state": self.from_state,
            "to_state": self.to_state,
            "event": self.event,
            "reason": self.reason,
            "at": self.at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationTransition":
        """
        功能：从字典反序列化状态迁移记录。

        输入：
        - data: 持久化后的状态迁移字典。

        输出：
        - ConversationTransition: 反序列化后的对象。

        调用情况：
        - 由 `DialogueState.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(
            from_state=data["from_state"],
            to_state=data["to_state"],
            event=data["event"],
            reason=data.get("reason"),
            at=data.get("at", time.time()),
        )


@dataclass(slots=True)
class TurnRoute:
    kind: str
    event: str
    reason: str | None = None
    semantic_kind: str | None = None
    at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """
        功能：把本轮路由记录序列化成字典。

        输入：
        - 无显式输入；依赖当前对象字段。

        输出：
        - Dict[str, Any]: 可持久化的路由记录字典。

        调用情况：
        - 由 `DialogueState.to_dict()` 调用。

        副作用：
        - 无。
        """
        return {
            "kind": self.kind,
            "event": self.event,
            "reason": self.reason,
            "semantic_kind": self.semantic_kind,
            "at": self.at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TurnRoute":
        """
        功能：从字典反序列化本轮路由记录。

        输入：
        - data: 持久化后的路由记录字典。

        输出：
        - TurnRoute: 反序列化后的对象。

        调用情况：
        - 由 `DialogueState.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(
            kind=data["kind"],
            event=data["event"],
            reason=data.get("reason"),
            semantic_kind=data.get("semantic_kind"),
            at=data.get("at", time.time()),
        )


@dataclass(slots=True)
class TaskOutcome:
    kind: str
    flow_id: str | None = None
    reason: str | None = None
    semantic_kind: str | None = None
    at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """
        功能：把 task 执行结果序列化成字典。

        输入：
        - 无显式输入；依赖当前对象字段。

        输出：
        - Dict[str, Any]: 可持久化的 task outcome 字典。

        调用情况：
        - 由 `DialogueState.to_dict()` 调用。

        副作用：
        - 无。
        """
        return {
            "kind": self.kind,
            "flow_id": self.flow_id,
            "reason": self.reason,
            "semantic_kind": self.semantic_kind,
            "at": self.at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskOutcome":
        """
        功能：从字典反序列化 task 执行结果。

        输入：
        - data: 持久化后的 task outcome 字典。

        输出：
        - TaskOutcome: 反序列化后的对象。

        调用情况：
        - 由 `DialogueState.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(
            kind=data["kind"],
            flow_id=data.get("flow_id"),
            reason=data.get("reason"),
            semantic_kind=data.get("semantic_kind"),
            at=data.get("at", time.time()),
        )


@dataclass(slots=True)
class Turn:
    turn_id: str
    user_message: UserMessage
    bot_messages: list[BotMessage]

    def to_dict(self) -> Dict[str, Any]:
        """
        功能：把单个对话 turn 序列化成字典。

        输入：
        - 无显式输入；依赖当前对象字段。

        输出：
        - Dict[str, Any]: 可持久化的 turn 字典。

        调用情况：
        - 由 `Session.to_dict()` 调用。

        副作用：
        - 无。
        """
        return {
            "turn_id": self.turn_id,
            "user_message": self.user_message.to_dict(),
            "bot_messages": [bot_message.to_dict() for bot_message in self.bot_messages],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Turn":
        """
        功能：从字典反序列化单个对话 turn。

        输入：
        - data: 持久化后的 turn 字典。

        输出：
        - Turn: 反序列化后的 turn 对象。

        调用情况：
        - 由 `Session.from_dict()` 和 `DialogueState.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(
            turn_id=data["turn_id"],
            user_message=UserMessage.from_dict(data["user_message"]),
            bot_messages=[BotMessage.from_dict(item) for item in data["bot_messages"]],
        )


@dataclass(slots=True)
class Session:
    session_id: str
    started_at: float
    last_activity_at: float
    closed_at: float | None = None
    turns: list[Turn] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        功能：把会话对象序列化成字典。

        输入：
        - 无显式输入；依赖当前对象字段。

        输出：
        - Dict[str, Any]: 可持久化的会话字典。

        调用情况：
        - 由 `DialogueState.to_dict()` 调用。

        副作用：
        - 无。
        """
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "closed_at": self.closed_at,
            "last_activity_at": self.last_activity_at,
            "turns": [turn.to_dict() for turn in self.turns],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """
        功能：从字典反序列化会话对象。

        输入：
        - data: 持久化后的会话字典。

        输出：
        - Session: 反序列化后的会话对象。

        调用情况：
        - 由 `DialogueState.from_dict()` 调用。

        副作用：
        - 无。
        """
        return cls(
            session_id=data["session_id"],
            started_at=data["started_at"],
            last_activity_at=data["last_activity_at"],
            closed_at=data.get("closed_at"),
            turns=[Turn.from_dict(turn_dict) for turn_dict in data["turns"]],
        )


@dataclass(slots=True)
class DialogueState:
    resident_id: str
    active_task: TaskContext | None = None
    paused_tasks: list[TaskContext] = field(default_factory=list)
    active_system_task: SystemContext | None = None
    focused_object: FocusedObject | None = None
    conversation_state: str = ConversationState.IDLE.value
    last_transition: ConversationTransition | None = None
    last_route: TurnRoute | None = None
    last_task_outcome: TaskOutcome | None = None
    sessions: list[Session] = field(default_factory=list)
    current_session_id: str | None = None
    pending_turn: Turn | None = None

    def to_dict(self) -> Dict[str, Any]:
        """
        功能：把完整的 DialogueState 序列化成持久化字典。

        输入：
        - 无显式输入；依赖当前对象字段。

        输出：
        - Dict[str, Any]: 可直接保存到仓储的状态字典。

        调用情况：
        - 由 repository、状态快照接口等调用。

        副作用：
        - 无。
        """
        return {
            "resident_id": self.resident_id,
            "active_task": self.active_task.to_dict() if self.active_task else None,
            "paused_tasks": [paused_task.to_dict() for paused_task in self.paused_tasks],
            "active_system_task": self.active_system_task.to_dict() if self.active_system_task else None,
            "focused_object": self.focused_object.to_dict() if self.focused_object else None,
            "conversation_state": self.conversation_state,
            "last_transition": self.last_transition.to_dict() if self.last_transition else None,
            "last_route": self.last_route.to_dict() if self.last_route else None,
            "last_task_outcome": self.last_task_outcome.to_dict() if self.last_task_outcome else None,
            "sessions": [session.to_dict() for session in self.sessions],
            "current_session_id": self.current_session_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueState":
        """
        功能：从持久化字典反序列化完整 DialogueState。

        输入：
        - data: 仓储读取出的状态字典。

        输出：
        - DialogueState: 反序列化后的状态聚合根。

        调用情况：
        - 由 repository 和状态快照保存逻辑调用。

        副作用：
        - 无。
        """
        return cls(
            resident_id=data["resident_id"],
            active_task=TaskContext.from_dict(data["active_task"]) if data.get("active_task") else None,
            paused_tasks=[TaskContext.from_dict(item) for item in data.get("paused_tasks", [])],
            active_system_task=SystemContext.from_dict(data["active_system_task"]) if data.get("active_system_task") else None,
            focused_object=FocusedObject.from_dict(data["focused_object"]) if data.get("focused_object") else None,
            conversation_state=data.get("conversation_state", ConversationState.IDLE.value),
            last_transition=ConversationTransition.from_dict(data["last_transition"]) if data.get("last_transition") else None,
            last_route=TurnRoute.from_dict(data["last_route"]) if data.get("last_route") else None,
            last_task_outcome=TaskOutcome.from_dict(data["last_task_outcome"]) if data.get("last_task_outcome") else None,
            sessions=[Session.from_dict(session) for session in data.get("sessions", [])],
            current_session_id=data.get("current_session_id"),
            pending_turn=Turn.from_dict(data["pending_turn"]) if data.get("pending_turn") else None,
        )

    def current_conversation_state(self) -> ConversationState:
        """
        功能：把当前字符串状态安全转换成 ConversationState 枚举。

        输入：
        - 无显式输入；依赖 `conversation_state` 字段。

        输出：
        - ConversationState: 当前状态枚举；非法值时回退为 IDLE。

        调用情况：
        - 由状态迁移和重置逻辑调用。

        副作用：
        - 无。
        """
        try:
            return ConversationState(self.conversation_state)
        except ValueError:
            return ConversationState.IDLE

    def transition_to(
        self,
        next_state: ConversationState,
        *,
        event: str,
        reason: str | None = None,
    ) -> None:
        """
        功能：把 conversation_state 迁移到指定状态，并记录 last_transition。

        输入：
        - next_state: 目标高层状态。
        - event: 触发迁移的事件名。
        - reason: 迁移原因说明。

        输出：
        - 无返回值；结果体现在状态字段变化上。

        调用情况：
        - 由状态机、session 管理和 runtime 管理逻辑广泛调用。

        副作用：
        - 会更新 `conversation_state` 和 `last_transition`。
        """
        previous_state = self.current_conversation_state().value
        self.conversation_state = next_state.value
        self.last_transition = ConversationTransition(
            from_state=previous_state,
            to_state=next_state.value,
            event=event,
            reason=reason,
        )

    def record_route(
        self,
        *,
        kind: str,
        event: str,
        reason: str | None = None,
        semantic_kind: str | None = None,
    ) -> None:
        """
        功能：记录当前轮次最终选择的高层轨道信息。

        输入：
        - kind: 轨道类型，如 task / knowledge / clarify / chitchat。
        - event: 本次路由事件名。
        - reason: 路由原因说明。
        - semantic_kind: 更细的语义分类。

        输出：
        - 无返回值。

        调用情况：
        - 由状态机和 runtime exit 逻辑调用。

        副作用：
        - 会更新 `last_route`。
        """
        self.last_route = TurnRoute(
            kind=kind,
            event=event,
            reason=reason,
            semantic_kind=semantic_kind,
        )

    def clear_last_route(self) -> None:
        """
        功能：清空上一轮路由记录。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由 `begin_turn()` 在新一轮开始时调用。

        副作用：
        - 会把 `last_route` 置空。
        """
        self.last_route = None

    def record_task_outcome(
        self,
        *,
        kind: str,
        flow_id: str | None = None,
        reason: str | None = None,
        semantic_kind: str | None = None,
    ) -> None:
        """
        功能：记录最近一次 task 执行结果。

        输入：
        - kind: outcome 类型。
        - flow_id: 当前关联的 flow_id。
        - reason: 结果原因说明。
        - semantic_kind: 当前轮次语义分类。

        输出：
        - 无返回值。

        调用情况：
        - 由状态机在 task 执行完成后调用。

        副作用：
        - 会更新 `last_task_outcome`。
        """
        self.last_task_outcome = TaskOutcome(
            kind=kind,
            flow_id=flow_id,
            reason=reason,
            semantic_kind=semantic_kind,
        )

    def clear_last_task_outcome(self) -> None:
        """
        功能：清空上一轮 task 执行结果记录。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由 `begin_turn()` 在新一轮开始时调用。

        副作用：
        - 会把 `last_task_outcome` 置空。
        """
        self.last_task_outcome = None

    def recompute_conversation_state(
        self,
        *,
        event: str,
        reason: str | None = None,
    ) -> ConversationState:
        """
        功能：根据当前 active_task / active_system_task / focused_object 重新推导高层状态。

        输入：
        - event: 本次重算触发事件名。
        - reason: 重算原因说明。

        输出：
        - ConversationState: 重算后的状态枚举。

        调用情况：
        - 由 task、session、focused object 相关修改方法复用。

        副作用：
        - 会更新 `conversation_state` 和 `last_transition`。
        """
        # 这里按“系统任务 > 业务任务 > focused object > idle”的优先级重算高层状态。
        if self.active_system_task is not None:
            if self.active_system_task.flow_id == "system_collect_information":
                next_state = ConversationState.CLARIFYING
            else:
                next_state = ConversationState.TRANSITIONING
        elif self.active_task is not None:
            next_state = ConversationState.ACTIVE_TASK
        elif self.focused_object is not None:
            next_state = ConversationState.FOCUSED_KNOWLEDGE
        else:
            next_state = ConversationState.IDLE

        self.transition_to(next_state, event=event, reason=reason)
        return next_state

    def mark_clarifying(self, *, event: str, reason: str | None = None) -> None:
        """
        功能：显式把当前高层状态标记为澄清态。

        输入：
        - event: 触发事件名。
        - reason: 原因说明。

        输出：
        - 无返回值。

        调用情况：
        - 保留给显式状态设置场景使用。

        副作用：
        - 会更新 `conversation_state` 和 `last_transition`。
        """
        self.transition_to(ConversationState.CLARIFYING, event=event, reason=reason)

    def mark_chitchat(self, *, event: str, reason: str | None = None) -> None:
        """
        功能：显式把当前高层状态标记为闲聊态。

        输入：
        - event: 触发事件名。
        - reason: 原因说明。

        输出：
        - 无返回值。

        调用情况：
        - 保留给显式状态设置场景使用。

        副作用：
        - 会更新 `conversation_state` 和 `last_transition`。
        """
        self.transition_to(ConversationState.CHITCHAT, event=event, reason=reason)

    def mark_focused_knowledge(self, *, event: str, reason: str | None = None) -> None:
        """
        功能：显式把当前高层状态标记为聚焦知识态。

        输入：
        - event: 触发事件名。
        - reason: 原因说明。

        输出：
        - 无返回值。

        调用情况：
        - 保留给显式状态设置场景使用。

        副作用：
        - 会更新 `conversation_state` 和 `last_transition`。
        """
        self.transition_to(ConversationState.FOCUSED_KNOWLEDGE, event=event, reason=reason)

    def mark_active_task(self, *, event: str, reason: str | None = None) -> None:
        """
        功能：显式把当前高层状态标记为任务进行态。

        输入：
        - event: 触发事件名。
        - reason: 原因说明。

        输出：
        - 无返回值。

        调用情况：
        - 保留给显式状态设置场景使用。

        副作用：
        - 会更新 `conversation_state` 和 `last_transition`。
        """
        self.transition_to(ConversationState.ACTIVE_TASK, event=event, reason=reason)

    def mark_transitioning(self, *, event: str, reason: str | None = None) -> None:
        """
        功能：显式把当前高层状态标记为过渡态。

        输入：
        - event: 触发事件名。
        - reason: 原因说明。

        输出：
        - 无返回值。

        调用情况：
        - 保留给显式状态设置场景使用。

        副作用：
        - 会更新 `conversation_state` 和 `last_transition`。
        """
        self.transition_to(ConversationState.TRANSITIONING, event=event, reason=reason)

    def start_active_task(self, task_context: TaskContext) -> None:
        """
        功能：启动一个新的 active task，并重算高层状态。

        输入：
        - task_context: 要设为当前任务的 TaskContext。

        输出：
        - 无返回值。

        调用情况：
        - 由 task 执行层在启动业务 flow 时调用。

        副作用：
        - 会更新 `active_task` 和高层状态。
        """
        self.active_task = task_context
        self.recompute_conversation_state(event="start_active_task", reason=task_context.flow_id)

    def end_active_task(self) -> None:
        """
        功能：结束当前 active task，并重算高层状态。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由 task 执行层在业务 flow 完成时调用。

        副作用：
        - 会清空 `active_task` 并重算状态。
        """
        self.active_task = None
        self.recompute_conversation_state(event="end_active_task")

    def cancel_active_task(self) -> None:
        """
        功能：取消当前 active task，并同步清理 active_system_task。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由 task cancel 场景调用。

        副作用：
        - 会清空 `active_task`、`active_system_task` 并重算状态。
        """
        self.active_task = None
        self.active_system_task = None
        self.recompute_conversation_state(event="cancel_active_task")

    def clear_paused_tasks(self) -> None:
        """
        功能：清空所有被打断的任务。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由 task 生命周期或 runtime reset 场景调用。

        副作用：
        - 会清空 `paused_tasks` 并重算状态。
        """
        self.paused_tasks = []
        self.recompute_conversation_state(event="clear_paused_tasks")

    def interrupt_active_task(self) -> None:
        """
        功能：把当前 active task 挂起到 paused_tasks。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由任务切换或打断场景调用。

        副作用：
        - 会移动 `active_task` 到 `paused_tasks` 并重算状态。
        """
        if self.active_task is not None:
            interrupted_flow_id = self.active_task.flow_id
            self.paused_tasks.append(self.active_task)
            self.active_task = None
            self.recompute_conversation_state(event="interrupt_active_task", reason=interrupted_flow_id)

    def resume_task(self, flow_id: str | None = None) -> bool:
        """
        功能：从 paused_tasks 中恢复一个任务为 active_task。

        输入：
        - flow_id: 指定要恢复的 flow_id；为空时恢复最近一个被打断的任务。

        输出：
        - bool: 恢复成功返回 True，否则返回 False。

        调用情况：
        - 由 task resume 场景调用。

        副作用：
        - 会修改 `paused_tasks`、`active_task` 并重算状态。
        """
        if not self.paused_tasks:
            return False

        if flow_id is None:
            self.active_task = self.paused_tasks.pop()
            self.recompute_conversation_state(event="resume_task", reason=self.active_task.flow_id)
            return True

        for paused_task in self.paused_tasks:
            if paused_task.flow_id == flow_id:
                self.active_task = paused_task
                self.paused_tasks.remove(paused_task)
                self.recompute_conversation_state(event="resume_task", reason=flow_id)
                return True

        return False

    def start_active_system_task(self, system_context: SystemContext) -> None:
        """
        功能：启动系统任务并重算高层状态。

        输入：
        - system_context: 要设为当前系统任务的上下文对象。

        输出：
        - 无返回值。

        调用情况：
        - 由 task 执行层在进入系统收集 flow 时调用。

        副作用：
        - 会更新 `active_system_task` 并重算状态。
        """
        self.active_system_task = system_context
        self.recompute_conversation_state(event="start_active_system_task", reason=system_context.flow_id)

    def end_active_system_task(self) -> None:
        """
        功能：结束当前系统任务并重算高层状态。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由系统收集 flow 完成时调用。

        副作用：
        - 会清空 `active_system_task` 并重算状态。
        """
        self.active_system_task = None
        self.recompute_conversation_state(event="end_active_system_task")

    def current_active_task(self) -> SystemContext | TaskContext | None:
        """
        功能：返回当前优先应视为“活跃任务”的上下文。

        输入：
        - 无。

        输出：
        - SystemContext | TaskContext | None: 优先返回系统任务，其次返回业务任务。

        调用情况：
        - 由执行层或状态观察逻辑调用。

        副作用：
        - 无。
        """
        return self.active_system_task or self.active_task

    def set_slots(self, slots: Dict[str, Any]) -> None:
        """
        功能：把槽位值合并到当前 active_task。

        输入：
        - slots: 要写入当前任务的槽位字典。

        输出：
        - 无返回值。

        调用情况：
        - 由 task 执行层和对象承接逻辑调用。

        副作用：
        - 会修改 `active_task.slots`。
        """
        if self.active_task is not None:
            self.active_task.slots.update(slots)

    def remove_slot(self, slot_name: str) -> None:
        """
        功能：从当前 active_task 中删除指定槽位。

        输入：
        - slot_name: 要删除的槽位名。

        输出：
        - 无返回值。

        调用情况：
        - 由 task 执行层在回退或重问场景调用。

        副作用：
        - 会修改 `active_task.slots`。
        """
        if self.active_task is None:
            raise ValueError("No active task available to remove slot from.")

        self.active_task.slots.pop(slot_name, None)

    def start_session(self) -> None:
        """
        功能：创建新的会话并设为当前会话。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由 `DialogueEngine._prepare_session()` 调用。

        副作用：
        - 会新增 `Session`、更新 `current_session_id` 并把高层状态切回 IDLE。
        """
        if self.current_session() is not None:
            return

        now = time.time()
        session_id = str(uuid.uuid4())
        self.sessions.append(
            Session(
                session_id=session_id,
                started_at=now,
                last_activity_at=now,
            )
        )
        self.current_session_id = session_id
        self.transition_to(ConversationState.IDLE, event="start_session")

    def current_session(self) -> Session | None:
        """
        功能：返回当前会话对象。

        输入：
        - 无。

        输出：
        - Session | None: 找到 current_session_id 对应会话则返回，否则返回 None。

        调用情况：
        - 由引擎、历史构建和 turn 提交逻辑广泛调用。

        副作用：
        - 无。
        """
        for session in self.sessions:
            if self.current_session_id == session.session_id:
                return session
        return None

    def close_session(self) -> None:
        """
        功能：关闭当前会话。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由会话超时切换逻辑调用。

        副作用：
        - 会更新当前 session 的 `closed_at` 并清空 `current_session_id`。
        """
        current_session = self.current_session()
        if current_session is None:
            return

        current_session.closed_at = time.time()
        self.current_session_id = None

    def reset_running_state_for_new_session(self) -> None:
        """
        功能：为新会话清理旧会话残留的运行时状态。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由会话超时切换逻辑调用。

        副作用：
        - 会重置 runtime state、清空当前会话 ID 和 pending_turn。
        """
        self.reset_runtime_state(event="reset_running_state_for_new_session")
        self.current_session_id = None
        self.pending_turn = None

    def begin_turn(self, message: UserMessage) -> None:
        """
        功能：开启一个新的 pending_turn，准备承接本轮机器人回复。

        输入：
        - message: 当前轮次的用户消息。

        输出：
        - 无返回值。

        调用情况：
        - 由 `DialogueEngine.hand_dialogue()` 在每轮开始时调用。

        副作用：
        - 会清空上一轮 route / task outcome，并设置 `pending_turn`。
        """
        if self.current_session() is None:
            return

        # 新一轮开始前，先清理上一轮留下的高层观测字段。
        self.clear_last_route()
        self.clear_last_task_outcome()
        self.pending_turn = Turn(
            turn_id=str(uuid.uuid4()),
            user_message=message,
            bot_messages=[],
        )

    def commit_turn(self) -> None:
        """
        功能：把 pending_turn 提交到当前会话历史中。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由 `DialogueEngine.hand_dialogue()` 在本轮处理结束后调用。

        副作用：
        - 会把 `pending_turn` 追加到当前 session 的 `turns`，随后清空 `pending_turn`。
        """
        current_session = self.current_session()
        if current_session is None or self.pending_turn is None:
            return

        current_session.turns.append(self.pending_turn)
        self.pending_turn = None

    def set_focused_object(self, focused_object: FocusedObject) -> None:
        """
        功能：设置当前 focused object，并重算高层状态。

        输入：
        - focused_object: 新的聚焦对象。

        输出：
        - 无返回值。

        调用情况：
        - 由对象消息处理、文本对象切换、状态恢复等场景调用。

        副作用：
        - 会更新 `focused_object` 并重算状态。
        """
        self.focused_object = focused_object
        focus_reason = focused_object.title or focused_object.id
        self.recompute_conversation_state(event="set_focused_object", reason=focus_reason)

    def clear_focused_object(self) -> None:
        """
        功能：清空当前 focused object，并重算高层状态。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由 runtime reset 或对象退出场景调用。

        副作用：
        - 会清空 `focused_object` 并重算状态。
        """
        self.focused_object = None
        self.recompute_conversation_state(event="clear_focused_object")

    def has_runtime_state(self) -> bool:
        """
        功能：判断当前是否存在可视作“上下文未退出”的运行时状态。

        输入：
        - 无。

        输出：
        - bool: 只要存在任务、系统任务、暂停任务或 focused object，就返回 True。

        调用情况：
        - 由 runtime exit / normalizer 等逻辑调用。

        副作用：
        - 无。
        """
        return (
            self.active_task is not None
            or bool(self.paused_tasks)
            or self.active_system_task is not None
            or self.focused_object is not None
        )

    def clear_runtime_state(self) -> None:
        """
        功能：清空任务和对象相关运行时状态，并按当前剩余字段重算高层状态。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - 由少量需要“清空但仍走重算逻辑”的场景调用。

        副作用：
        - 会清空任务/对象相关字段并重算状态。
        """
        self.active_task = None
        self.active_system_task = None
        self.paused_tasks = []
        self.focused_object = None
        self.recompute_conversation_state(event="clear_runtime_state")

    def reset_runtime_state(
        self,
        *,
        event: str,
        reason: str | None = None,
    ) -> None:
        """
        功能：强制重置 runtime state，并把高层状态直接落回 IDLE。

        输入：
        - event: 本次重置事件名。
        - reason: 重置原因说明。

        输出：
        - 无返回值。

        调用情况：
        - 由 runtime exit、对象切换重置、跨 session 切换等场景调用。

        副作用：
        - 会清空 `active_task`、`active_system_task`、`paused_tasks`、`focused_object`，
          并直接重写 `conversation_state / last_transition`。
        """
        previous_state = self.current_conversation_state().value
        self.active_task = None
        self.active_system_task = None
        self.paused_tasks = []
        self.focused_object = None
        self.conversation_state = ConversationState.IDLE.value
        self.last_transition = ConversationTransition(
            from_state=previous_state,
            to_state=ConversationState.IDLE.value,
            event=event,
            reason=reason,
        )

    def runtime_state_labels(self) -> list[str]:
        """
        功能：把当前 runtime state 压缩成便于展示和调试的标签列表。

        输入：
        - 无。

        输出：
        - list[str]: 当前任务、暂停任务、系统任务和 focused object 的摘要标签。

        调用情况：
        - 由调试、观察和日志展示逻辑调用。

        副作用：
        - 无。
        """
        labels: list[str] = []

        if self.active_task is not None:
            labels.append(f"current_task:{self.active_task.flow_id}")
        if self.paused_tasks:
            labels.append(f"paused_tasks:{len(self.paused_tasks)}")
        if self.active_system_task is not None:
            labels.append("active_system_task")
        if self.focused_object is not None:
            focused_title = self.focused_object.title or self.focused_object.id
            labels.append(f"focused_object:{focused_title}")

        return labels
