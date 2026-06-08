from atguigu.chitchat.responder import ChitchatResponder
from atguigu.domain.messages import BotMessage, UserMessage
from atguigu.domain.state import DialogueState, Turn
from atguigu.prompt.history_builder import HistoryBuilder


class ChitchatHandler:

    def __init__(self, responder: ChitchatResponder | None = None):
        self.responder = responder or ChitchatResponder()

    def handle(
        self,
        state: DialogueState | None = None,
        user_message: UserMessage | None = None,
        recent_turns: list[Turn] | None = None,
    ) -> list[BotMessage]:
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
