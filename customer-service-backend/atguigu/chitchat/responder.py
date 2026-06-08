from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.messages import BotMessage
from atguigu.infrastructure.llm import llm
from atguigu.prompt.loader import load_prompt


class ChitchatResponder:
    """
    功能：为闲聊轨生成轻量回复，并在 LLM 不可用时提供兜底话术。
    """

    def respond(self, user_message: str | None, history: str = "") -> list[BotMessage]:
        """
        功能：生成一条闲聊回复。

        输入：
        - user_message: 当前用户文本，可为空。
        - history: 最近多轮历史文本。

        输出：
        - list[BotMessage]: 闲聊轨返回的消息列表。

        调用情况：
        - `ChitchatHandler.handle()`

        副作用：
        - 无状态写入；会调用闲聊提示词和 LLM。
        """
        normalized_message = (user_message or "").strip()
        if not normalized_message:
            return [BotMessage(text="你好，我在。你想先聊聊，还是需要我帮你处理物业问题？")]

        prompt_text = load_prompt("chitchat_respond")
        prompt_template = PromptTemplate.from_template(prompt_text, template_format="jinja2")
        chain = prompt_template | llm | StrOutputParser()

        try:
            content = chain.invoke(
                {
                    "user_message": normalized_message,
                    "history": history,
                }
            ).strip()
        except Exception:
            content = self._fallback(normalized_message)

        if not content:
            content = self._fallback(normalized_message)

        return [BotMessage(text=content)]

    def _fallback(self, user_message: str) -> str:
        """
        功能：在闲聊模型调用失败或返回空时提供兜底回复。

        输入：
        - user_message: 当前用户文本。

        输出：
        - str: 兜底闲聊话术。

        调用情况：
        - `respond()`

        副作用：
        - 无。
        """
        if not user_message.strip():
            return "你好，我在。你可以先聊两句，也可以直接告诉我你想处理什么物业问题。"

        return "我在听。你可以直接说想法，也可以告诉我你现在想处理什么物业问题。"
