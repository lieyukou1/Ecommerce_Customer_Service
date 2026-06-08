from atguigu.domain.messages import UserMessage, ProcessResult
from atguigu.domain.state import DialogueState, Turn
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_state_repository import DialogueStateRepository


class DialogueService:
    def __init__(self,
                 dialogue_state_repository: DialogueStateRepository,
                 dialogue_engine: DialogueEngine):
        self.dialogue_engine = dialogue_engine
        self.dialogue_state_repository = dialogue_state_repository

    async def process_message(self, user_message: UserMessage) -> ProcessResult:
        """

        """
        # 1.加载
        dialogue_state = await self.dialogue_state_repository.load(user_message.resident_id)

        # 2.处理
        process_result = await self.dialogue_engine.hand_dialogue(dialogue_state, user_message)

        # 3.保存
        await self.dialogue_state_repository.save(dialogue_state)

        return process_result

    async def load_history(self, resident_id: str) -> list[Turn]:
        dialogue_state = await self.dialogue_state_repository.load(resident_id)
        return self._select_history_turns(dialogue_state)

    @staticmethod
    def _select_history_turns(dialogue_state: DialogueState) -> list[Turn]:
        current_session = dialogue_state.current_session()
        if current_session is not None:
            return current_session.turns

        if dialogue_state.sessions:
            return dialogue_state.sessions[-1].turns

        return []
