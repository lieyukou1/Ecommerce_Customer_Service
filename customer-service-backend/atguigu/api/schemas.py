from pydantic import BaseModel, Field


class ChatObject(BaseModel):
    type: str
    id: str
    title: str | None = None
    attributes: dict = Field(default=dict)


class ChatRequest(BaseModel):
    resident_id: str
    message_id: str | None = None
    text: str | None = None
    object: ChatObject | None = None


class ChatBotMessage(BaseModel):
    text: str | None = None
    object: ChatObject | None = None


class ChatResponse(BaseModel):
    resident_id: str
    message_id: str
    messages: list[ChatBotMessage]


class HistoryMessage(BaseModel):
    role: str  # user or bot
    text: str | None = None
    object: ChatObject | None = None


class HistoryResponse(BaseModel):
    resident_id: str
    messages: list[HistoryMessage]


class DialogueStateSnapshotRequest(BaseModel):
    resident_id: str
    state: dict


class DialogueStateSnapshotResponse(BaseModel):
    resident_id: str
    state: dict
