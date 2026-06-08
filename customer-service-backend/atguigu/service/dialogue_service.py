from atguigu.domain.messages import ProcessResult, UserMessage
from atguigu.domain.state import DialogueState, Turn
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_state_repository import DialogueStateRepository


class DialogueService:
    def __init__(
        self,
        dialogue_state_repository: DialogueStateRepository,
        dialogue_engine: DialogueEngine,
    ):
        """
        功能：构造对话服务，连接状态仓储和对话引擎。

        输入：
        - dialogue_state_repository: 负责加载和保存住户对话状态的仓储实例。
        - dialogue_engine: 负责执行对话主链的引擎实例。

        输出：
        - 无返回值；初始化服务对象依赖。

        调用情况：
        - 由依赖注入装配层创建，供 API 路由复用。

        副作用：
        - 无；只保存依赖引用。
        """
        self.dialogue_engine = dialogue_engine
        self.dialogue_state_repository = dialogue_state_repository

    async def process_message(self, user_message: UserMessage) -> ProcessResult:
        """
        功能：处理单条用户消息，串起“加载状态 -> 引擎处理 -> 保存状态”三步。

        输入：
        - user_message: 已转换为领域层对象的用户消息。

        输出：
        - ProcessResult: 本轮处理后的机器人消息及消息元数据。

        调用情况：
        - 由 `api.router.chat_router.chat()` 调用，是文本/对象消息进入主链的 service 入口。

        副作用：
        - 会从仓储读取并回写 DialogueState。
        """
        # 先按住户加载已有运行时状态，作为本轮对话处理上下文。
        dialogue_state = await self.dialogue_state_repository.load(user_message.resident_id)
        # 把消息交给引擎，完成路由、状态迁移和业务执行。
        process_result = await self.dialogue_engine.hand_dialogue(dialogue_state, user_message)
        # 本轮处理结束后持久化最新状态，保证下轮对话能续上上下文。
        await self.dialogue_state_repository.save(dialogue_state)
        return process_result

    async def load_history(self, resident_id: str) -> list[Turn]:
        """
        功能：读取指定住户当前应展示的历史 turn 列表。

        输入：
        - resident_id: 住户标识。

        输出：
        - list[Turn]: 当前会话或最近会话的 turn 列表。

        调用情况：
        - 由 `api.router.chat_router.chat_history()` 调用。

        副作用：
        - 无状态修改；只读取仓储。
        """
        dialogue_state = await self.dialogue_state_repository.load(resident_id)
        return self._select_history_turns(dialogue_state)

    async def load_state(self, resident_id: str) -> DialogueState:
        """
        功能：读取指定住户的完整 DialogueState。

        输入：
        - resident_id: 住户标识。

        输出：
        - DialogueState: 当前持久化状态。

        调用情况：
        - 由 `api.router.chat_router.chat_state()` 调用。

        副作用：
        - 无。
        """
        return await self.dialogue_state_repository.load(resident_id)

    async def reset_state(self, resident_id: str) -> DialogueState:
        """
        功能：将指定住户的状态重置为全新空状态并保存。

        输入：
        - resident_id: 住户标识。

        输出：
        - DialogueState: 重置后的初始状态。

        调用情况：
        - 由 `api.router.chat_router.reset_chat_state()` 调用。

        副作用：
        - 会覆盖保存该住户原有状态。
        """
        dialogue_state = DialogueState(resident_id=resident_id)
        await self.dialogue_state_repository.save(dialogue_state)
        return dialogue_state

    async def save_state_snapshot(self, resident_id: str, state_payload: dict) -> DialogueState:
        """
        功能：用外部给定的状态字典构造并保存 DialogueState。

        输入：
        - resident_id: 住户标识，始终以后端传入值为准。
        - state_payload: 外部提交的状态快照字典。

        输出：
        - DialogueState: 合并默认值并反序列化后的状态对象。

        调用情况：
        - 由 `api.router.chat_router.save_chat_state()` 调用。

        副作用：
        - 会直接覆盖保存仓储中的该住户状态。
        """
        # 先拿一份最小默认状态，避免外部快照缺字段时无法反序列化。
        base_state = DialogueState(resident_id=resident_id).to_dict()
        merged_state = {
            **base_state,
            **state_payload,
            # resident_id 不允许由外部 payload 篡改，始终以后端显式入参为准。
            "resident_id": resident_id,
        }
        dialogue_state = DialogueState.from_dict(merged_state)
        await self.dialogue_state_repository.save(dialogue_state)
        return dialogue_state

    @staticmethod
    def _select_history_turns(dialogue_state: DialogueState) -> list[Turn]:
        """
        功能：从完整状态里挑出前端应该展示的历史 turn 集合。

        输入：
        - dialogue_state: 已加载的完整对话状态。

        输出：
        - list[Turn]: 优先返回当前会话 turn；没有当前会话时回退到最近一次历史会话。

        调用情况：
        - 由 `load_history()` 调用。

        副作用：
        - 无。
        """
        current_session = dialogue_state.current_session()
        if current_session is not None:
            return current_session.turns

        # 没有 current_session 时，回退展示最近一次已存在的会话历史。
        if dialogue_state.sessions:
            return dialogue_state.sessions[-1].turns

        return []
