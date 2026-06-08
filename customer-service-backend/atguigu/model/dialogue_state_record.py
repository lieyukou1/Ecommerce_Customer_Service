from sqlalchemy import String, TEXT
from sqlalchemy.orm import Mapped, mapped_column

from atguigu.model.base import Base


class DialogueStateRecord(Base):
    """
    dialogue_states 表：每个用户一行，state_json 存储完整对话状态。
    """
    __tablename__ = 'dialogue_states'
    resident_id: Mapped[str] = mapped_column(primary_key=True)
    state_json: Mapped[str] = mapped_column(TEXT, nullable=False, default={})
