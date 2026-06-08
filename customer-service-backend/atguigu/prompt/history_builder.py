from typing import Any, Dict, List

from atguigu.domain.messages import BotMessage, FocusedObject, MessageType, UserMessage
from atguigu.domain.state import Turn


class HistoryBuilder:
    """
    功能：把领域层消息与 turn 历史渲染成提示词可消费的文本。
    """

    @staticmethod
    def build(turns: List[Turn]) -> str:
        """
        功能：把多轮 turn 历史展开成 `USER/BOT` 文本串。

        输入：
        - turns: 最近若干轮对话历史。

        输出：
        - str: 供 planner、clarify、knowledge、chitchat 使用的历史文本。

        调用情况：
        - `TurnPlanner._build_history()`
        - `KnowledgeHandler.handle()`
        - `ClarifyResponder._build_prompt_payload()`
        - `ChitchatHandler.handle()`

        副作用：
        - 无。
        """
        msgs = []
        for turn in turns:
            user_message = turn.user_message
            user_message_str = HistoryBuilder._render_user_message(user_message)
            msgs.append(f"USER: {user_message_str}")

            for message in turn.bot_messages:
                bot_message_str = HistoryBuilder._render_bot_message(message)
                msgs.append(f"BOT: {bot_message_str}")

        return "\n".join(msgs)

    @classmethod
    def _render_user_message(cls, user_message: UserMessage) -> str:
        """
        功能：把领域层 UserMessage 渲染成可读文本。

        输入：
        - user_message: 当前用户消息对象。

        输出：
        - str: 文本消息或对象消息的渲染结果。

        调用情况：
        - `build()`
        - 多个 handler/responder 构造提示词时复用。

        副作用：
        - 无。
        """
        if user_message.type is MessageType.TEXT:
            return HistoryBuilder._render_text_msg(user_message.text)
        return HistoryBuilder._render_obj_msg(user_message.object)

    @classmethod
    def _render_text_msg(cls, text: str) -> str:
        """
        功能：清洗普通文本消息。

        输入：
        - text: 原始文本内容。

        输出：
        - str: 去首尾空白后的文本。

        调用情况：
        - `_render_user_message()`
        - `_render_bot_message()`

        副作用：
        - 无。
        """
        return text.strip()

    @classmethod
    def _render_obj_msg(cls, object: FocusedObject) -> str:
        """
        功能：把对象消息渲染成结构化文本。

        输入：
        - object: 当前对象消息。

        输出：
        - str: 包含 type、id、title、attributes 的结构化文本。

        调用情况：
        - `_render_user_message()`
        - `_render_bot_message()`

        副作用：
        - 无。
        """
        object_id: str = object.id
        object_type: str = "工单对象" if object.type == "work_order" else "服务项目对象"
        title: str = object.title
        attributes: Dict[str, Any] = object.attributes
        attributes_str: str = " ".join([f"{key}={value}" for key, value in attributes.items()])

        return f"[type={object_type}, id={object_id}, title={title}, attributes={attributes_str}]"

    @classmethod
    def _render_bot_message(cls, message: BotMessage) -> str:
        """
        功能：把 BotMessage 渲染成提示词文本。

        输入：
        - message: 机器人消息对象。

        输出：
        - str: 文本消息直接展开；对象消息按对象格式展开。

        调用情况：
        - `build()`

        副作用：
        - 无。
        """
        if message.text:
            return HistoryBuilder._render_text_msg(message.text)
        return HistoryBuilder._render_obj_msg(message.object)
