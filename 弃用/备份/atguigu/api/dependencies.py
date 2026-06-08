from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.engine.builder import build_dialogue_engine
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.infrastructure import database
from atguigu.repository.dialogue_state_repository import DialogueStateRepository
from atguigu.service.dialogue_service import DialogueService

_dialogue_engine: DialogueEngine | None = None


def init_dialogue_engine():
    global _dialogue_engine
    _dialogue_engine = build_dialogue_engine()  # 构建引擎的方法


async def get_session():
    async with database.async_session() as session:
        yield session


async def get_dialogue_engine():
    return _dialogue_engine


async def get_dialogue_state_repository(session: AsyncSession = Depends(get_session)):
    return DialogueStateRepository(session=session)


async def get_dialogue_service(
        dialogue_state_repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
        dialogue_engine: DialogueEngine = Depends(get_dialogue_engine)
) -> DialogueService:
    return DialogueService(
        dialogue_engine=dialogue_engine,
        dialogue_state_repository=dialogue_state_repository
    )
