from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.engine.builder import build_dialogue_engine
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.infrastructure import database
from atguigu.repository.dialogue_state_repository import DialogueStateRepository
from atguigu.service.dialogue_service import DialogueService

_dialogue_engine: DialogueEngine | None = None


def init_dialogue_engine():
    """
    功能：初始化全局唯一的 DialogueEngine 实例。

    输入：
    - 无。

    输出：
    - 无返回值；把引擎实例写入模块级缓存。

    调用情况：
    - `api.app.lifespan()`

    副作用：
    - 会构建并覆盖模块级 `_dialogue_engine`。
    """
    global _dialogue_engine
    _dialogue_engine = build_dialogue_engine()


async def get_session():
    """
    功能：为单个请求提供数据库会话。

    输入：
    - 无。

    输出：
    - AsyncSession: 当前请求作用域的异步数据库会话。

    调用情况：
    - FastAPI 依赖注入链。

    副作用：
    - 会打开并在请求结束后关闭数据库会话。
    """
    async with database.async_session() as session:
        yield session


async def get_dialogue_engine():
    """
    功能：返回已初始化的全局 DialogueEngine。

    输入：
    - 无。

    输出：
    - DialogueEngine | None: 当前缓存的引擎实例。

    调用情况：
    - `get_dialogue_service()`

    副作用：
    - 无。
    """
    return _dialogue_engine


async def get_dialogue_state_repository(session: AsyncSession = Depends(get_session)):
    """
    功能：为请求构造状态仓储。

    输入：
    - session: 当前请求的数据库会话。

    输出：
    - DialogueStateRepository: 基于当前 session 的仓储实例。

    调用情况：
    - `get_dialogue_service()`

    副作用：
    - 无。
    """
    return DialogueStateRepository(session=session)


async def get_dialogue_service(
    dialogue_state_repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
    dialogue_engine: DialogueEngine = Depends(get_dialogue_engine),
) -> DialogueService:
    """
    功能：为路由层构造对话服务对象。

    输入：
    - dialogue_state_repository: 当前请求的状态仓储。
    - dialogue_engine: 当前全局对话引擎。

    输出：
    - DialogueService: 已组装好的对话服务。

    调用情况：
    - 路由层通过 FastAPI 依赖注入调用。

    副作用：
    - 无。
    """
    return DialogueService(
        dialogue_engine=dialogue_engine,
        dialogue_state_repository=dialogue_state_repository,
    )
