"""

消息类型：两种
UserMessage(用户)
BotMessage(机器人)

to_dict:将实例对象转成字典对象
from_dict:将字典对象转成实例对象

"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List


class MessageType(Enum):
    TEXT = "text"
    OBJECT = "object"


@dataclass(slots=True)
class FocusedObject:
    """
    聚焦对象
    """
    id: str
    type: str
    title: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "attributes": dict(self.attributes)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FocusedObject":
        return cls(
            id=data["id"],
            type=data["type"],
            title=data.get("title", ""),
            attributes=data.get("attributes", {})
        )


@dataclass(slots=True)
class UserMessage:
    resident_id: str
    message_id: str
    type: MessageType
    text: str | None = None
    object: FocusedObject | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'resident_id': self.resident_id,
            'message_id': self.message_id,
            'type': self.type.value,
            'text': self.text,
            'object': self.object.to_dict() if self.object else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserMessage":
        return cls(
            resident_id=data["resident_id"],
            message_id=data["message_id"],
            type=MessageType(data["type"]),
            text=data.get("text"),
            object=FocusedObject.from_dict(data["object"]) if data.get('object') else None,
        )


@dataclass(slots=True)
class BotMessage:
    text: str | None = None
    object: FocusedObject | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'text': self.text,
            'object': self.object.to_dict() if self.object else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BotMessage":
        return cls(
            text=data.get("text"),
            object=FocusedObject.from_dict(data["object"]) if data.get('object') else None,
        )


@dataclass(slots=True)
class ProcessResult:
    resident_id: str
    message_id: str
    messages: List[BotMessage]
