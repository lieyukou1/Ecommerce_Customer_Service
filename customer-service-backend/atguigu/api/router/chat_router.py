import uuid

from fastapi import APIRouter, Depends

from atguigu.api.dependencies import get_dialogue_service
from atguigu.api.schemas import (
    ChatBotMessage,
    ChatObject,
    ChatRequest,
    ChatResponse,
    DialogueStateSnapshotRequest,
    DialogueStateSnapshotResponse,
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
    """
    功能：处理前端发来的单轮对话请求，并返回本轮机器人回复。

    输入：
    - chat_request: 前端提交的文本或对象消息，包含住户 ID、消息 ID 和可选对象信息。
    - service: 由 FastAPI 依赖注入的对话服务实例。

    输出：
    - ChatResponse: 面向前端的统一响应对象，包含本轮机器人消息列表。

    调用情况：
    - FastAPI `POST /api/chat` 路由入口。

    副作用：
    - 会触发完整的对话主链处理，并由 service 层落库对话状态。
    """
    # 先把接口层请求转换成领域层消息对象，统一后续主链输入形态。
    user_message = _build_user_message(chat_request)
    # 交给 service 层完成状态加载、引擎处理和状态保存。
    process_result = await service.process_message(user_message)
    # 最后把领域层处理结果封装成接口层响应。
    return _build_chat_response(process_result)


@router.get("/api/chat/history")
async def chat_history(
    resident_id: str,
    service: DialogueService = Depends(get_dialogue_service),
) -> HistoryResponse:
    """
    功能：查询指定住户当前可见的聊天历史。

    输入：
    - resident_id: 住户标识，用于定位该住户的对话状态。
    - service: 由 FastAPI 依赖注入的对话服务实例。

    输出：
    - HistoryResponse: 将最近会话中的 turn 列表展平后的历史消息结果。

    调用情况：
    - FastAPI `GET /api/chat/history` 路由入口。

    副作用：
    - 无状态修改；只读取已保存的对话状态。
    """
    turns = await service.load_history(resident_id)
    return _build_history_response(resident_id, turns)


@router.get("/api/chat/state")
async def chat_state(
    resident_id: str,
    service: DialogueService = Depends(get_dialogue_service),
) -> DialogueStateSnapshotResponse:
    """
    功能：读取指定住户当前完整的对话状态快照。

    输入：
    - resident_id: 住户标识。
    - service: 由 FastAPI 依赖注入的对话服务实例。

    输出：
    - DialogueStateSnapshotResponse: 序列化后的完整运行时状态。

    调用情况：
    - FastAPI `GET /api/chat/state` 路由入口。

    副作用：
    - 无状态修改；只读取仓储中的状态快照。
    """
    dialogue_state = await service.load_state(resident_id)
    return _build_state_snapshot_response(dialogue_state)


@router.put("/api/chat/state")
async def save_chat_state(
    request: DialogueStateSnapshotRequest,
    service: DialogueService = Depends(get_dialogue_service),
) -> DialogueStateSnapshotResponse:
    """
    功能：用外部传入的状态快照覆盖保存指定住户的对话状态。

    输入：
    - request: 包含 resident_id 和 state 字典的状态快照请求。
    - service: 由 FastAPI 依赖注入的对话服务实例。

    输出：
    - DialogueStateSnapshotResponse: 保存后的状态快照。

    调用情况：
    - FastAPI `PUT /api/chat/state` 路由入口。

    副作用：
    - 会直接重建并保存指定住户的 DialogueState。
    """
    dialogue_state = await service.save_state_snapshot(request.resident_id, request.state)
    return _build_state_snapshot_response(dialogue_state)


@router.delete("/api/chat/state")
async def reset_chat_state(
    resident_id: str,
    service: DialogueService = Depends(get_dialogue_service),
) -> DialogueStateSnapshotResponse:
    """
    功能：重置指定住户的对话状态为全新初始状态。

    输入：
    - resident_id: 住户标识。
    - service: 由 FastAPI 依赖注入的对话服务实例。

    输出：
    - DialogueStateSnapshotResponse: 重置后的空状态快照。

    调用情况：
    - FastAPI `DELETE /api/chat/state` 路由入口。

    副作用：
    - 会清空并覆盖保存该住户当前对话状态。
    """
    dialogue_state = await service.reset_state(resident_id)
    return _build_state_snapshot_response(dialogue_state)


def _build_user_message(chat_request: ChatRequest) -> UserMessage:
    """
    功能：把接口层请求对象转换成领域层 UserMessage。

    输入：
    - chat_request: 前端提交的聊天请求，可能是文本消息，也可能携带对象点击信息。

    输出：
    - UserMessage: 统一的领域层消息对象，供 service 和 engine 主链消费。

    调用情况：
    - 由 `chat()` 在进入 service 层前调用。

    副作用：
    - 无外部副作用；若请求未提供 message_id，会在这里生成新的 UUID。
    """
    return UserMessage(
        resident_id=chat_request.resident_id,
        # 前端未传 message_id 时，后端补一个 UUID，保证每条消息都有稳定标识。
        message_id=chat_request.message_id if chat_request.message_id else str(uuid.uuid4()),
        # 文本优先视作文本消息，否则视作对象消息。
        type=MessageType.TEXT if chat_request.text else MessageType.OBJECT,
        text=chat_request.text,
        # 前端若携带对象点击信息，要转换成领域层 FocusedObject 进入主链。
        object=FocusedObject(
            id=chat_request.object.id,
            type=chat_request.object.type,
            title=chat_request.object.title,
            attributes=chat_request.object.attributes,
        ) if chat_request.object else None,
    )


def _build_chat_response(process_result: ProcessResult) -> ChatResponse:
    """
    功能：把领域层 ProcessResult 转换成前端可消费的聊天响应。

    输入：
    - process_result: 引擎完成一轮处理后返回的领域层结果对象。

    输出：
    - ChatResponse: 含住户 ID、消息 ID 和机器人消息列表的接口层响应。

    调用情况：
    - 由 `chat()` 在 service 处理完成后调用。

    副作用：
    - 无；仅做对象转换。
    """
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
    """
    功能：把 turn 级历史记录展平成前端展示所需的消息列表。

    输入：
    - resident_id: 当前查询的住户标识。
    - turns: 从状态中挑出的会话 turn 列表。

    输出：
    - HistoryResponse: 用户消息和机器人消息按时序拼接后的历史响应。

    调用情况：
    - 由 `chat_history()` 在 service 返回 turn 列表后调用。

    副作用：
    - 无；仅做历史展示结构转换。
    """
    messages: list[HistoryMessage] = []

    for turn in turns:
        # 每个 turn 先追加用户消息，再顺序追加该 turn 下的全部机器人回复。
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


def _build_state_snapshot_response(dialogue_state) -> DialogueStateSnapshotResponse:
    """
    功能：把领域层 DialogueState 包装成状态快照接口响应。

    输入：
    - dialogue_state: 当前住户的完整运行时状态对象。

    输出：
    - DialogueStateSnapshotResponse: 以字典形式暴露的状态快照。

    调用情况：
    - 由 `chat_state()`、`save_chat_state()`、`reset_chat_state()` 调用。

    副作用：
    - 无；仅做序列化封装。
    """
    return DialogueStateSnapshotResponse(
        resident_id=dialogue_state.resident_id,
        state=dialogue_state.to_dict(),
    )


def _build_chat_object(focused_object: FocusedObject | None) -> ChatObject | None:
    """
    功能：把领域层 FocusedObject 转换成接口层 ChatObject。

    输入：
    - focused_object: 可能为空的领域层对象上下文。

    输出：
    - ChatObject | None: 前端可展示的对象结构；无对象时返回 None。

    调用情况：
    - 由 `_build_chat_response()`、`_build_history_response()` 复用。

    副作用：
    - 无；仅做对象转换。
    """
    if focused_object is None:
        return None

    return ChatObject(
        type=focused_object.type,
        id=focused_object.id,
        title=focused_object.title,
        attributes=focused_object.attributes,
    )
