import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.infrastructure.llm import llm
from atguigu.plan.turn_plan import ClarifyReason
from atguigu.prompt.history_builder import HistoryBuilder
from atguigu.prompt.loader import load_prompt


class ClarifyResponder:

    async def respond(self, state: DialogueState,
                      reason: ClarifyReason) -> list[BotMessage]:
        """

        """
        message = state.pending_turn.user_message
        clarify_message = self.build_clarify_message(reason=reason, state=state)
        user_message = HistoryBuilder._render_user_message(user_message=message)
        history = HistoryBuilder.build(state.current_session().turns[-10:])
        focused_object = json.dumps(
            state.focused_object.to_dict(),
            ensure_ascii=False,
        ) if state.focused_object is not None else None

        prompt_text = load_prompt("clarify_respond")
        prompt_template = PromptTemplate.from_template(template=prompt_text, template_format="jinja2")

        chain = prompt_template | llm | StrOutputParser()

        result = await chain.ainvoke({
            "user_message": user_message,
            "history": history,
            "focused_object": focused_object,
            "clarify_message": clarify_message,
            "reason": reason.value
        })

        return [BotMessage(text=result)]

    def build_clarify_message(
            self,
            reason: ClarifyReason,
            state: DialogueState,
    ) -> str:
        if reason is ClarifyReason.MULTIPLE_TRACKS:
            return "你这次同时提到了多个方向。我们先处理一个，你想先办业务还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_FOCUSED_OBJECT:
            return "请先告诉我你想看哪条工单，或者先从右侧选中一个工单或服务项目，我再继续帮你处理。"

        if reason is ClarifyReason.MISSING_KNOWLEDGE_INTENT:
            return "你是想了解工单信息、服务项目信息，还是想咨询物业费、装修报备、停车或宠物管理这类规则呢？"

        if reason is ClarifyReason.MISSING_TRACK:
            return "你是想先处理业务问题，还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_TASK_COMMANDS:
            return "你这次是想办理什么业务呢？比如查工单状态、看处理进度、提交催办、发起投诉，或者咨询服务项目详情。"

        if reason is ClarifyReason.OBJECT_REQUIRES_INTENT:
            focused_object = state.focused_object
            if focused_object is not None and focused_object.type == "work_order":
                return "我已经收到这条工单了。你想查当前状态、看处理进度、提交催办，还是发起投诉呢？"
            if focused_object is not None and focused_object.type == "service_item":
                return "我已经收到这个服务项目了。你想了解收费、办理方式、服务说明，还是当前可预约状态呢？"

        return "我还需要再确认一下你的意思，你可以换个更具体的说法告诉我。"
