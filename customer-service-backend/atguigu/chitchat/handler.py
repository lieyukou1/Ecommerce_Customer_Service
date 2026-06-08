from atguigu.chitchat.responder import ChitchatResponder
from atguigu.domain.messages import BotMessage, UserMessage
from atguigu.domain.state import DialogueState, Turn
from atguigu.prompt.history_builder import HistoryBuilder


class ChitchatHandler:
    """
    功能：承接 chitchat 轨请求，整理输入后交给闲聊回复器。
    """

    def __init__(self, responder: ChitchatResponder | None = None):
        """
        功能：构造闲聊处理器。

        输入：
        - responder: 可选闲聊回复器；为空时使用默认回复器。

        输出：
        - 无返回值；初始化依赖。

        调用情况：
        - 装配层创建，供文本轨的 chitchat 分支调用。

        副作用：
        - 无。
        """
        self.responder = responder or ChitchatResponder()

    def handle(
        self,
        state: DialogueState | None = None,
        user_message: UserMessage | None = None,
        recent_turns: list[Turn] | None = None,
    ) -> list[BotMessage]:
        """
        功能：处理一轮闲聊请求，补齐消息和历史后生成回复。

        输入：
        - state: 当前运行时状态，可为空。
        - user_message: 显式传入的用户消息；为空时尝试从 pending_turn 读取。
        - recent_turns: 显式传入的最近历史；为空时尝试从当前会话读取。

        输出：
        - list[BotMessage]: 闲聊轨生成的消息列表。

        调用情况：
        - `TextTurnHandler._execute_context()` 的 chitchat 分支。

        副作用：
        - 无状态写入。
        """
        resolved_message = user_message
        if resolved_message is None and state is not None and state.pending_turn is not None:
            resolved_message = state.pending_turn.user_message

        if recent_turns is None and state is not None and state.current_session() is not None:
            recent_turns = state.current_session().turns[-10:]

        rendered_message = (
            HistoryBuilder._render_user_message(resolved_message)
            if resolved_message is not None
            else None
        )
        history = HistoryBuilder.build(recent_turns or [])

        return self.responder.respond(user_message=rendered_message, history=history)
