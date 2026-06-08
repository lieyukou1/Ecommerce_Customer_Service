import uuid
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field

from atguigu.domain.contexts import TaskContext, SystemContext
from atguigu.domain.messages import FocusedObject, UserMessage, BotMessage


@dataclass(slots=True)
class Turn:
    turn_id: str
    user_message: UserMessage
    bot_messages: List[BotMessage]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "user_message": self.user_message.to_dict(),
            "bot_messages": [bot_message.to_dict() for bot_message in self.bot_messages],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Turn":
        return cls(
            turn_id=data["turn_id"],
            user_message=UserMessage.from_dict(data["user_message"]),
            bot_messages=[BotMessage.from_dict(bot_message_dict) for bot_message_dict in data["bot_messages"]],
        )


@dataclass(slots=True)
class Session:
    session_id: str
    started_at: float
    last_activity_at: float
    closed_at: float | None = None
    turns: List[Turn] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "closed_at": self.closed_at,
            "last_activity_at": self.last_activity_at,
            "turns": [turn.to_dict() for turn in self.turns],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        return cls(
            session_id=data["session_id"],
            started_at=data["started_at"],
            closed_at=data.get("closed_at"),
            last_activity_at=data["last_activity_at"],
            turns=[Turn.from_dict(turn_dict) for turn_dict in data["turns"]]
        )


@dataclass(slots=True)
class DialogueState:
    resident_id: str
    active_task: TaskContext | None = None  # 当前执行的业务任务
    paused_tasks: list[TaskContext] = field(default_factory=list)  # 当期暂停的业务任务（多个）
    active_system_task: SystemContext | None = None  # 当前执行的系统流程
    focused_object: FocusedObject | None = None
    sessions: list[Session] = field(default_factory=list)  # 当前用户的所有会话都存储起来
    current_session_id: str | None = None  # 当前用户的session的sessionID
    pending_turn: Turn | None = None  # turn会话的暂存区（变量：内存中缓冲区）

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resident_id": self.resident_id,
            "active_task": self.active_task.to_dict() if self.active_task else None,
            "paused_tasks": [paused_task.to_dict() for paused_task in self.paused_tasks],
            "active_system_task": self.active_system_task.to_dict() if self.active_system_task else None,
            "focused_object": self.focused_object.to_dict() if self.focused_object else None,
            "sessions": [session.to_dict() for session in self.sessions],
            "current_session_id": self.current_session_id,
            # "pending_turn": self.pending_turn.to_dict() if self.pending_turn else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueState":
        return cls(
            resident_id=data["resident_id"],
            active_task=TaskContext.from_dict(data.get("active_task")) if data.get("active_task") else None,
            paused_tasks=[TaskContext.from_dict(paused_task) for paused_task in data.get("paused_tasks")],
            active_system_task=SystemContext.from_dict(data.get("active_system_task")) if data.get(
                "active_system_task") else None,
            focused_object=FocusedObject.from_dict(data.get("focused_object")) if data.get("focused_object") else None,
            sessions=[Session.from_dict(session) for session in data.get("sessions")],
            current_session_id=data.get("current_session_id"),
            pending_turn=Turn.from_dict(data.get("pending_turn")) if data.get("pending_turn") else None,
        )

    # -----------------------任务相关-----------------------

    def start_active_task(self, task_context: TaskContext):
        """
        启动业务任务
        """
        self.active_task = task_context

    def end_active_task(self):
        """
        结束当前活跃任务
        """
        self.active_task = None

    def cancel_active_task(self):
        """
        取消当前活跃任务与活跃系统流程
        """
        self.active_task = None
        self.active_system_task = None

    def clear_paused_tasks(self):
        self.paused_tasks = []

    def interrupt_active_task(self):
        """
        打断当前活跃任务
        """
        if self.active_task:
            self.paused_tasks.append(self.active_task)
            self.active_task = None

    def resume_task(self, flow_id: str | None = None) -> bool:
        if not self.paused_tasks:
            return False

        if not flow_id:
            self.active_task = self.paused_tasks.pop()
            return True

        for paused_task in self.paused_tasks:
            if paused_task.flow_id == flow_id:
                self.active_task = paused_task
                self.paused_tasks.remove(paused_task)
                return True

        return False

    def start_active_system_task(self, system_context: SystemContext):
        """
        启动系统流程
        """
        self.active_system_task = system_context

    def end_active_system_task(self):
        """
        关闭系统流程
        """
        self.active_system_task = None

    def current_active_task(self):
        """
        确定当前正在执行的任务
        """
        return self.active_system_task or self.active_task

    # -----------------------槽位相关-----------------------

    def set_slots(self, slots: Dict[str, Any]):
        """

        """

        if self.active_task is not None:
            self.active_task.slots.update(slots)

    def remove_slot(self, slot_name: str):
        """

        """

        if self.active_task is None:
            raise ValueError("当前没有活跃的业务任务，无法删除 slot")

        self.active_task.slots.pop(slot_name, None)

    # -----------------------session相关-----------------------

    def start_session(self):
        """
        创建一个新会话
        """
        if self.current_session() is None:
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

    def current_session(self):
        """
        确定当前会话
        """
        for session in self.sessions:
            if self.current_session_id == session.session_id:
                return session

        return None

    def close_session(self):
        """
        关闭当前会话
        """
        if self.current_session_id is not None:
            self.current_session().closed_at = time.time()
            self.current_session_id = None

    def reset_running_state_for_new_session(self):
        """
        重置会话运行时状态
        """
        self.clear_runtime_state()
        self.current_session_id = None
        self.pending_turn = None

    # -----------------------turn相关-----------------------

    def begin_turn(self, message: UserMessage):
        """
        开启新轮次
        """
        if self.current_session():
            self.pending_turn = Turn(
                turn_id=str(uuid.uuid4()),
                user_message=message,
                bot_messages=[]
            )

    def commit_turn(self):
        if self.current_session():
            self.current_session().turns.append(self.pending_turn)
            self.pending_turn = None

    # --------------FocusedObject相关的--------------------------
    def set_focused_object(self, focused_object: FocusedObject):
        self.focused_object = focused_object

    def clear_focused_object(self):
        self.focused_object = None

    def has_runtime_state(self) -> bool:
        return (
            self.active_task is not None
            or bool(self.paused_tasks)
            or self.active_system_task is not None
            or self.focused_object is not None
        )

    def clear_runtime_state(self):
        self.active_task = None
        self.active_system_task = None
        self.paused_tasks = []
        self.focused_object = None

    def runtime_state_labels(self) -> list[str]:
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
