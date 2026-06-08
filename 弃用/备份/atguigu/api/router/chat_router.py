import uuid

from fastapi import APIRouter, Depends

from atguigu.api.dependencies import get_dialogue_service
from atguigu.api.schemas import (
    ChatBotMessage,
    ChatObject,
    ChatRequest,
    ChatResponse,
    HistoryMessage,
    HistoryResponse,
)
from atguigu.domain.messages import (
    BotMessage,
    FocusedObject,
    MessageType,
    ProcessResult,
    UserMessage,
)
from atguigu.domain.state import Turn
from atguigu.service.dialogue_service import DialogueService

router = APIRouter()


@router.post("/api/chat")
async def chat(
    chat_request: ChatRequest,
    service: DialogueService = Depends(get_dialogue_service),
) -> ChatResponse:
    user_message = _build_user_message(chat_request)
    process_result = await service.process_message(user_message)
    return _build_chat_response(process_result)


@router.get("/api/chat/history")
async def chat_history(
    resident_id: str,
    service: DialogueService = Depends(get_dialogue_service),
) -> HistoryResponse:
    turns = await service.load_history(resident_id)
    return _build_history_response(resident_id, turns)


def _build_user_message(chat_request: ChatRequest) -> UserMessage:
    return UserMessage(
        resident_id=chat_request.resident_id,
        message_id=chat_request.message_id if chat_request.message_id else str(uuid.uuid4()),
        type=MessageType.TEXT if chat_request.text else MessageType.OBJECT,
        text=chat_request.text,
        object=FocusedObject(
            id=chat_request.object.id,
            type=chat_request.object.type,
            title=chat_request.object.title,
            attributes=chat_request.object.attributes,
        ) if chat_request.object else None,
    )


def _build_chat_response(process_result: ProcessResult) -> ChatResponse:
    return ChatResponse(
        resident_id=process_result.resident_id,
        message_id=process_result.message_id,
        messages=[
            ChatBotMessage(
                text=bot_message.text,
                object=_build_chat_object(bot_message.object),
            )
            for bot_message in process_result.messages
        ],
    )


def _build_history_response(resident_id: str, turns: list[Turn]) -> HistoryResponse:
    messages: list[HistoryMessage] = []

    for turn in turns:
        messages.append(
            HistoryMessage(
                role="user",
                text=turn.user_message.text,
                object=_build_chat_object(turn.user_message.object),
            )
        )
        messages.extend(
            HistoryMessage(
                role="bot",
                text=bot_message.text,
                object=_build_chat_object(bot_message.object),
            )
            for bot_message in turn.bot_messages
        )

    return HistoryResponse(
        resident_id=resident_id,
        messages=messages,
    )


def _build_chat_object(focused_object: FocusedObject | None) -> ChatObject | None:
    if focused_object is None:
        return None

    return ChatObject(
        type=focused_object.type,
        id=focused_object.id,
        title=focused_object.title,
        attributes=focused_object.attributes,
    )
