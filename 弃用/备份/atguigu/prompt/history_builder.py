from typing import List, Dict, Any

from atguigu.domain.messages import UserMessage, MessageType, FocusedObject, BotMessage
from atguigu.domain.state import Turn


class HistoryBuilder:
    """
    1. 将用户消息的UserMessage对象序列化为字符串---->"USER: 我准备查询工单信息"
    2. 将历史对话的Q(UserMessage)A(BotMessage)对象序列化为字符串："USER: 我想查询处理进度\n BOT: 好的，先提供工单编号"
    """

    @staticmethod
    def build(turns: List[Turn]) -> str:
        msgs = []
        for turn in turns:
            # 1.user
            user_message = turn.user_message
            user_message_str = HistoryBuilder._render_user_message(user_message)
            msgs.append(f'USER: {user_message_str}')

            # 2.bot
            for message in turn.bot_messages:
                bot_message_str = HistoryBuilder._render_bot_message(message)
                msgs.append(f'BOT: {bot_message_str}')

        return '\n'.join(msgs)

    @classmethod
    def _render_user_message(cls, user_message: UserMessage) -> str:
        """
        渲染用户消息
        """
        if user_message.type is MessageType.TEXT:
            return HistoryBuilder._render_text_msg(user_message.text)
        else:
            return HistoryBuilder._render_obj_msg(user_message.object)

    @classmethod
    def _render_text_msg(cls, text: str) -> str:
        """

        """
        return text.strip()

    @classmethod
    def _render_obj_msg(cls, object: FocusedObject) -> str:
        """

        """
        id: str = object.id
        type: str = "工单对象" if object.type == "work_order" else "服务项目对象"
        title: str = object.title
        attributes: Dict[str, Any] = object.attributes
        attributes_str: str = " ".join([f'{key}={value}' for key, value in attributes.items()])

        return f'[type={type}, id={id}, title={title}, attributes={attributes_str}]'

    @classmethod
    def _render_bot_message(cls, message: BotMessage) -> str:
        """

        """
        if message.text:
            return HistoryBuilder._render_text_msg(message.text)
        else:
            return HistoryBuilder._render_obj_msg(message.object)
