import json

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.domain.state import DialogueState
from atguigu.model.dialogue_state_record import DialogueStateRecord


class DialogueStateRepository:
    """
    功能：负责对话状态的数据库读写。
    """

    def __init__(self, session: AsyncSession):
        """
        功能：构造状态仓储。

        输入：
        - session: 当前请求作用域内的异步数据库会话。

        输出：
        - 无返回值；保存数据库会话依赖。

        调用情况：
        - `get_dialogue_state_repository()`

        副作用：
        - 无。
        """
        self.session = session

    async def load(self, resident_id: str) -> DialogueState:
        """
        功能：按住户 ID 读取完整对话状态。

        输入：
        - resident_id: 住户 ID。

        输出：
        - DialogueState: 已保存的完整状态；数据库中不存在时返回新的空状态。

        调用情况：
        - `DialogueService.process_message()`
        - `DialogueService.load_history()`
        - `DialogueService.load_state()`

        副作用：
        - 无；只读取数据库。
        """
        sql = select(DialogueStateRecord).where(DialogueStateRecord.resident_id == resident_id)
        result = await self.session.execute(sql)
        state_record = result.scalar_one_or_none()

        if state_record:
            state_dict = json.loads(state_record.state_json)
            return DialogueState.from_dict(state_dict)

        return DialogueState(resident_id=resident_id)

    async def save(self, state: DialogueState):
        """
        功能：把完整对话状态持久化到数据库。

        输入：
        - state: 待保存的完整对话状态。

        输出：
        - 无返回值。

        调用情况：
        - `DialogueService.process_message()`
        - `DialogueService.reset_state()`
        - `DialogueService.save_state_snapshot()`

        副作用：
        - 会执行数据库 upsert 并提交事务。
        """
        state_json = json.dumps(state.to_dict())

        # 使用 MySQL 的 on duplicate key update，把“新增或覆盖保存”统一成一条语句。
        insert_stmt = insert(DialogueStateRecord).values(
            resident_id=state.resident_id,
            state_json=state_json,
        )
        update_stmt = insert_stmt.on_duplicate_key_update(
            state_json=insert_stmt.inserted.state_json
        )

        await self.session.execute(update_stmt)
        await self.session.commit()
