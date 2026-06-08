from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.messages import BotMessage
from atguigu.infrastructure.llm import llm
from atguigu.knowledge.provider import KnowledgeChunk
from atguigu.prompt.loader import load_prompt


class KnowledgeResponder:

    def respond(
        self,
        user_message: str | None,
        history: str,
        knowledge_chunks: list[KnowledgeChunk],
        intent_descriptions: list[str],
    ) -> list[BotMessage]:
        normalized_message = (user_message or "").strip()
        knowledge_content = self._build_knowledge_content(knowledge_chunks)

        if not normalized_message:
            return [BotMessage(text=self._fallback(knowledge_chunks, intent_descriptions))]

        if knowledge_chunks and all(chunk.provider_id.startswith("api.") for chunk in knowledge_chunks):
            return [BotMessage(text=self._structured_reply(knowledge_chunks))]

        prompt_text = load_prompt("knowledge_respond")
        prompt_template = PromptTemplate.from_template(prompt_text, template_format="jinja2")
        chain = prompt_template | llm | StrOutputParser()

        try:
            content = chain.invoke(
                {
                    "user_message": normalized_message,
                    "history": history,
                    "knowledge_content": knowledge_content,
                    "intent_descriptions": "、".join(intent_descriptions),
                }
            ).strip()
        except Exception:
            content = self._fallback(knowledge_chunks, intent_descriptions)

        if not content:
            content = self._fallback(knowledge_chunks, intent_descriptions)

        return [BotMessage(text=content)]

    def _build_knowledge_content(self, knowledge_chunks: list[KnowledgeChunk]) -> str:
        if not knowledge_chunks:
            return ""

        parts: list[str] = []
        for chunk in knowledge_chunks:
            parts.append(f"[{chunk.title}]\n{chunk.content}")
        return "\n\n".join(parts)

    def _structured_reply(self, knowledge_chunks: list[KnowledgeChunk]) -> str:
        if not knowledge_chunks:
            return "我先帮你整理一下当前信息，不过现在还缺少足够的上下文。"

        primary_chunk = knowledge_chunks[0]
        primary_reply = self._render_api_chunk(primary_chunk)
        if primary_reply:
            return primary_reply

        lines = ["我先根据当前信息帮你整理一下："]
        for chunk in knowledge_chunks[:2]:
            lines.append(f"{chunk.title}：")
            lines.extend(chunk.content.splitlines())
        lines.append("如果你想继续追问更具体的细节，可以直接接着问我。")
        return "\n".join(lines)

    def _render_api_chunk(self, chunk: KnowledgeChunk) -> str | None:
        metadata = chunk.metadata or {}
        object_type = metadata.get("object_type")
        if object_type == "service_item":
            return self._render_service_item_reply(chunk.content)
        if object_type == "work_order":
            return self._render_work_order_reply(chunk.content)
        return None

    def _render_service_item_reply(self, content: str) -> str:
        fields = self._parse_chunk_lines(content)
        title = fields.get("服务项目标题") or fields.get("服务项目ID") or "这个服务项目"
        price = fields.get("price")
        description = fields.get("description")
        service_status = fields.get("service_status")

        parts = [f"关于{title}，我先帮你整理一下："]

        details: list[str] = []
        if price:
            details.append(f"收费是 {price} 元")
        if service_status:
            details.append(f"当前状态是“{service_status}”")
        if description:
            details.append(f"服务说明是：{description}")

        if details:
            parts.append("；".join(details) + "。")
        else:
            parts.append("我这边已经拿到当前项目的上下文了。")

        parts.append("你可以继续问收费、办理方式、服务说明，或者换一个项目继续问。")
        return "\n".join(parts)

    def _render_work_order_reply(self, content: str) -> str:
        fields = self._parse_chunk_lines(content)
        work_order_id = fields.get("工单ID")
        status = fields.get("status")
        summary = fields.get("summary")
        appointment_time = fields.get("appointment_time")
        amount = fields.get("amount")

        title = f"工单 {work_order_id}" if work_order_id else "这条工单"
        parts = [f"关于{title}，我先帮你看一下："]

        details: list[str] = []
        if status:
            details.append(f"当前状态是“{status}”")
        if summary:
            details.append(f"工单内容是：{summary}")
        if appointment_time:
            details.append(f"预约时间是 {appointment_time}")
        if amount:
            details.append(f"相关金额是 {amount}")

        if details:
            parts.append("；".join(details) + "。")
        else:
            parts.append("我这边已经拿到当前工单的上下文了。")

        parts.append("你可以继续问处理进度、催办、投诉，或者换一条工单继续聊。")
        return "\n".join(parts)

    @staticmethod
    def _parse_chunk_lines(content: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or "：" not in line:
                continue
            key, value = line.split("：", 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                fields[key] = value
        return fields

    def _fallback(
        self,
        knowledge_chunks: list[KnowledgeChunk],
        intent_descriptions: list[str],
    ) -> str:
        if knowledge_chunks:
            lines = ["我先根据当前掌握的信息整理一下："]
            for chunk in knowledge_chunks[:2]:
                lines.append(f"{chunk.title}：{chunk.content}")
            lines.append("如果你想继续追问更细的条件或办理步骤，可以直接告诉我。")
            return "\n".join(lines)

        if intent_descriptions:
            return f"这类问题我可以继续帮你看，不过现在缺少足够信息。你可以再具体说一下，重点是“{'、'.join(intent_descriptions)}”里的哪一项。"

        return "你可以再具体说一下想咨询哪方面的物业信息，我再继续帮你整理。"
