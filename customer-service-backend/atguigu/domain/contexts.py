from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(slots=True)
class TaskContext:
    flow_id: str
    step_id: str | None = None
    slots: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "step_id": self.step_id,
            "slots": self.slots,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskContext":
        return cls(
            flow_id=data["flow_id"],
            step_id=data.get("step_id"),
            slots=dict(data.get("slots", {}))
        )


@dataclass(slots=True)
class SystemContext:
    flow_id: str
    step_id: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "step_id": self.step_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemContext":
        clz = FLOW_ID_TO_CONTEXT_CLASS[data["flow_id"]]
        return clz(**data)


@dataclass(slots=True)
class StartedSystemContext(SystemContext):
    started_flow_id: str = ""
    started_flow_name: str = ""


@dataclass(slots=True)
class InterruptedSystemContext(SystemContext):
    interrupted_flow_id: str = ""
    interrupted_flow_name: str = ""
    started_flow_id: str = ""
    started_flow_name: str = ""


@dataclass(slots=True)
class CanceledSystemContext(SystemContext):
    canceled_flow_id: str = ""
    canceled_flow_name: str = ""


@dataclass(slots=True)
class ResumedSystemContext(SystemContext):
    resumed_flow_id: str = ""
    resumed_flow_name: str = ""


@dataclass(slots=True)
class CollectedSystemContext(SystemContext):
    slot_name: str = ""
    response: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CompletedSystemContext(SystemContext):
    pass


FLOW_ID_TO_CONTEXT_CLASS: Dict[str, Any] = {
    "system_task_started": StartedSystemContext,
    "system_task_resumed": ResumedSystemContext,
    "system_collect_information": CollectedSystemContext,
    "system_task_interrupted": InterruptedSystemContext,
    "system_task_canceled": CanceledSystemContext,
    "system_completed": CompletedSystemContext
}
