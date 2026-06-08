from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.messages import BotMessage
from atguigu.infrastructure.llm import llm
from atguigu.prompt.loader import load_prompt


class ChitchatResponder:

    def respond(self, user_message: str | None, history: str = "") -> list[BotMessage]:
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
        lowered = user_message.lower()

        if any(keyword in lowered for keyword in ["你好", "您好", "嗨", "在吗", "hi", "hello"]):
            return "你好，我在。今天想聊两句，还是要我帮你看下物业这边的事？"

        if any(keyword in lowered for keyword in ["你是谁", "你叫什么", "你是干嘛的", "介绍一下你自己"]):
            return "我是小区智能管家，可以陪你简单聊聊，也可以帮你处理和查询物业相关的问题。"

        if any(keyword in lowered for keyword in ["谢谢", "多谢", "thank"]):
            return "不客气，有需要你就直接说。"

        if any(keyword in lowered for keyword in ["再见", "拜拜", "bye"]):
            return "好，先这样。有事再叫我。"

        return "我在听。你可以直接说想法，也可以告诉我你现在想处理什么物业问题。"
