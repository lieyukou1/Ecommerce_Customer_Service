import json
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.domain.state import DialogueState
from atguigu.model.dialogue_state_record import DialogueStateRecord


class DialogueStateRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def load(self, resident_id: str) -> DialogueState:
        """

        """
        # 1.定义sql
        sql = select(DialogueStateRecord).where(DialogueStateRecord.resident_id == resident_id)

        # 2.执行sql
        result = await self.session.execute(sql)

        # 3.获取结果
        state = result.scalar_one_or_none()

        if state:
            state_dict = json.loads(state.state_json)
            return DialogueState.from_dict(state_dict)

        return DialogueState(resident_id=resident_id)

    async def save(self, state: DialogueState):
        """
        写操作(插入、修改)
        传统：插入之前先查询该条件（resident_id）对应的记录是否存在，如果不存在 则插入，反之修改
        进阶：负责将插入sql直接升级为修改sql(主键重复机制判断)
        :return:
        """
        # 1.得到DialogueState的json
        state_json = json.dumps(state.to_dict())

        # 2.定义插入的sql语句
        insert_stmt = insert(DialogueStateRecord).values(
            resident_id=state.resident_id, state_json=state_json
        )

        # 3.升级update的sql语句
        update_stmt = insert_stmt.on_duplicate_key_update(
            state_json=insert_stmt.inserted.state_json
        )

        # 4.执行sql
        await self.session.execute(update_stmt)

        # 5.提交
        await self.session.commit()
