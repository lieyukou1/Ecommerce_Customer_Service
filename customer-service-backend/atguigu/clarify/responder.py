import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.infrastructure.llm import llm
from atguigu.plan.turn_plan import ClarifyContext, ClarifyReason
from atguigu.prompt.history_builder import HistoryBuilder
from atguigu.prompt.loader import load_prompt


ACTIVE_TASK_REASONS = {
    ClarifyReason.MISSING_TRACK,
    ClarifyReason.MISSING_TASK_COMMANDS,
    ClarifyReason.INVALID_TASK_COMMANDS,
}


class ClarifyResponder:
    """
    功能：为澄清轨构造最终回复，优先给出上下文感强的引导话术。
    """

    async def respond(
        self,
        state: DialogueState,
        clarify_context: ClarifyContext | None,
    ) -> list[BotMessage]:
        """
        功能：基于澄清上下文和当前状态生成一条澄清回复。

        输入：
        - state: 当前运行时状态。
        - clarify_context: 当前澄清上下文，可为空。

        输出：
        - list[BotMessage]: 澄清轨返回的消息列表。

        调用情况：
        - `TextTurnHandler._respond_validation_failure()`
        - `ObjectTurnHandler._respond_object_requires_intent()`

        副作用：
        - 无状态写入；只调用澄清提示词和 LLM。
        """
        prompt_text = load_prompt("clarify_respond")
        prompt_template = PromptTemplate.from_template(template=prompt_text, template_format="jinja2")
        chain = prompt_template | llm | StrOutputParser()

        result = await chain.ainvoke(self._build_prompt_payload(state, clarify_context))
        return [BotMessage(text=result)]

    def _build_prompt_payload(
        self,
        state: DialogueState,
        clarify_context: ClarifyContext | None,
    ) -> dict[str, str | None]:
        """
        功能：把当前澄清所需的上下文压缩成提示词输入字典。

        输入：
        - state: 当前运行时状态。
        - clarify_context: 当前澄清上下文，可为空。

        输出：
        - dict[str, str | None]: 传给澄清提示词模板的字段集合。

        调用情况：
        - `respond()`

        副作用：
        - 无。
        """
        message = state.pending_turn.user_message
        return {
            "user_message": HistoryBuilder._render_user_message(user_message=message),
            "history": HistoryBuilder.build(state.current_session().turns[-10:]),
            "focused_object": self._serialize_focused_object(state),
            "clarify_message": self.build_clarify_message(
                clarify_context=clarify_context,
                state=state,
            ),
            "reason": self._resolve_reason_value(clarify_context),
        }

    @staticmethod
    def _serialize_focused_object(state: DialogueState) -> str | None:
        """
        功能：把 focused object 序列化成提示词可用文本。

        输入：
        - state: 当前运行时状态。

        输出：
        - str | None: focused object 的 JSON 文本；无对象时返回 None。

        调用情况：
        - `_build_prompt_payload()`

        副作用：
        - 无。
        """
        focused_object = state.focused_object
        if focused_object is None:
            return None
        return json.dumps(focused_object.to_dict(), ensure_ascii=False)

    @staticmethod
    def _resolve_reason_value(clarify_context: ClarifyContext | None) -> str:
        """
        功能：把 ClarifyReason 规整成提示词里稳定可用的字符串值。

        输入：
        - clarify_context: 当前澄清上下文，可为空。

        输出：
        - str: reason 的字符串值；缺失时返回 `unknown`。

        调用情况：
        - `_build_prompt_payload()`

        副作用：
        - 无。
        """
        if clarify_context is None or clarify_context.reason is None:
            return "unknown"
        return clarify_context.reason.value

    def build_clarify_message(
        self,
        clarify_context: ClarifyContext | None,
        state: DialogueState,
    ) -> str:
        """
        功能：为本轮澄清挑选一条最合适的引导消息。

        输入：
        - clarify_context: 当前澄清上下文，可为空。
        - state: 当前运行时状态。

        输出：
        - str: 本轮澄清话术。

        调用情况：
        - `_build_prompt_payload()`

        副作用：
        - 无。
        """
        reason = clarify_context.reason if clarify_context is not None else None

        # 先看是否有“当前任务/对象上下文强相关”的澄清提示。
        contextual_message = self._build_contextual_clarify_message(
            state=state,
            clarify_context=clarify_context,
            reason=reason,
        )
        if contextual_message is not None:
            return contextual_message

        # 再回退到按 reason 模板化生成的兜底澄清。
        reason_message = self._build_reason_clarify_message(state, reason)
        if reason_message is not None:
            return reason_message

        return "我还需要再确认一下你的意思。你可以换个更具体的说法告诉我。"

    def _build_contextual_clarify_message(
        self,
        *,
        state: DialogueState,
        clarify_context: ClarifyContext | None,
        reason: ClarifyReason | None,
    ) -> str | None:
        """
        功能：优先生成和当前任务/对象上下文强绑定的澄清消息。

        输入：
        - state: 当前运行时状态。
        - clarify_context: 当前澄清上下文，可为空。
        - reason: 当前澄清原因，可为空。

        输出：
        - str | None: 命中强上下文提示时返回消息，否则返回 None。

        调用情况：
        - `build_clarify_message()`

        副作用：
        - 无。
        """
        if reason in ACTIVE_TASK_REASONS:
            active_task_message = self._build_active_task_followup_message(state)
            if active_task_message is not None:
                return active_task_message

        if clarify_context is not None and clarify_context.is_object_intent():
            return self._build_object_intent_message(state)

        return None

    def _build_reason_clarify_message(
        self,
        state: DialogueState,
        reason: ClarifyReason | None,
    ) -> str | None:
        """
        功能：按 ClarifyReason 生成通用澄清消息。

        输入：
        - state: 当前运行时状态。
        - reason: 当前澄清原因，可为空。

        输出：
        - str | None: 命中原因模板时返回消息，否则返回 None。

        调用情况：
        - `build_clarify_message()`

        副作用：
        - 无。
        """
        if reason is ClarifyReason.MULTIPLE_TRACKS:
            return "你这次同时提到了多个方向。我们先处理一个，你想先办理业务，还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_FOCUSED_OBJECT:
            return "请先告诉我你想看哪条工单，或者先从右侧选中一个工单或服务项目，我再继续帮你处理。"

        if reason is ClarifyReason.MISSING_KNOWLEDGE_INTENT:
            return self._build_missing_knowledge_intent_message(state)

        if reason is ClarifyReason.MISSING_TRACK:
            return self._build_missing_track_clarify_message(state)

        if reason is ClarifyReason.MISSING_TASK_COMMANDS:
            return self._build_missing_task_commands_message(state)

        if reason is ClarifyReason.INVALID_TASK_COMMANDS:
            return self._build_invalid_task_commands_message(state)

        if reason is ClarifyReason.MULTIPLE_TASK_FLOWS:
            return "你这句话里同时带了多个办理方向。我先处理一个，你是想查状态、看进度、催办，还是发起投诉？"

        if reason is ClarifyReason.UNKNOWN_TASK_FLOW:
            return "我还没法直接识别你要进入的办理流程。你可以明确说一下是要查状态、看进度、催办、投诉，还是咨询服务项目详情。"

        if reason is ClarifyReason.INVALID_DIRECTIVE:
            return "我理解你是在调整当前上下文。你如果是想退出当前这段，可以直接说“退出”或“先这样”。"

        return None

    def _build_missing_knowledge_intent_message(self, state: DialogueState) -> str:
        """
        功能：针对“知识轨已命中但具体知识点不明确”生成引导。

        输入：
        - state: 当前运行时状态。

        输出：
        - str: 结合当前对象类型生成的追问话术。

        调用情况：
        - `_build_reason_clarify_message()`

        副作用：
        - 无。
        """
        object_type = self._get_focused_object_type(state)
        if object_type == "work_order":
            return "你是想了解这条工单的状态、进度和费用说明，还是想继续办理催办、投诉这类业务？"
        if object_type == "service_item":
            return "你是想了解这个服务项目的收费、办理方式和服务说明，还是想继续办理相关业务？"
        return "你是想了解工单信息、服务项目信息，还是想咨询物业费、装修报备、停车或宠物管理这类规则呢？"

    def _build_object_intent_message(self, state: DialogueState) -> str | None:
        """
        功能：当用户已选中对象但意图不明时，给出对象导向型追问。

        输入：
        - state: 当前运行时状态。

        输出：
        - str | None: 针对对象类型的引导消息；没有对象时返回 None。

        调用情况：
        - `_build_contextual_clarify_message()`

        副作用：
        - 无。
        """
        object_type = self._get_focused_object_type(state)
        if object_type == "work_order":
            return "我已经收到这条工单了。你想查当前状态、看处理进度、提交催办，还是发起投诉呢？"

        if object_type == "service_item":
            return "我已经收到这个服务项目了。你想了解收费、办理方式、服务说明，还是当前可预约状态呢？"

        return None

    def _build_missing_track_clarify_message(self, state: DialogueState) -> str:
        """
        功能：当 planner 没有明确轨道时，结合当前对象上下文做一轮追问。

        输入：
        - state: 当前运行时状态。

        输出：
        - str: 缺轨道时使用的澄清消息。

        调用情况：
        - `_build_reason_clarify_message()`

        副作用：
        - 无。
        """
        focused_object_message = self._build_missing_track_message(state)
        if focused_object_message is not None:
            return focused_object_message
        return "你是想先处理业务问题，还是先咨询信息呢？"

    def _build_missing_task_commands_message(self, state: DialogueState) -> str:
        """
        功能：当 task 轨被选中但没产出命令时，提示用户把业务目标说清。

        输入：
        - state: 当前运行时状态。

        输出：
        - str: 引导用户明确 task 目标的话术。

        调用情况：
        - `_build_reason_clarify_message()`

        副作用：
        - 无。
        """
        focused_object_message = self._build_focused_object_guidance(state)
        if focused_object_message is not None:
            return focused_object_message
        return "你这次是想办理什么业务呢？比如查工单状态、看处理进度、提交催办、发起投诉，或者咨询服务项目详情。"

    def _build_invalid_task_commands_message(self, state: DialogueState) -> str:
        """
        功能：当 task commands 非法时，提示用户改用更清楚的业务表达。

        输入：
        - state: 当前运行时状态。

        输出：
        - str: task command 校验失败时的兜底提示。

        调用情况：
        - `_build_reason_clarify_message()`

        副作用：
        - 无。
        """
        focused_object_message = self._build_focused_object_guidance(state)
        if focused_object_message is not None:
            return focused_object_message
        return "我这边还没法直接按这句话继续处理。你可以说得更具体一点，比如说明要查状态、看进度、催办、投诉，或者补充当前要填写的信息。"

    def _build_active_task_followup_message(self, state: DialogueState) -> str | None:
        """
        功能：在任务进行中优先把澄清拉回当前 task 生命周期。

        输入：
        - state: 当前运行时状态。

        输出：
        - str | None: 命中当前任务追问时返回消息，否则返回 None。

        调用情况：
        - `_build_contextual_clarify_message()`

        副作用：
        - 无。
        """
        active_task = state.active_task
        active_system_task = state.active_system_task
        if active_task is None:
            return None

        slot_name = getattr(active_system_task, "slot_name", None) if active_system_task is not None else None
        slot_message = self._build_slot_followup_message(state, slot_name)
        if slot_message is not None:
            return slot_message

        if active_task.flow_id == "work_order_urge_submission":
            return "我们现在还在处理工单催办。你可以直接补充催办原因，或者如果不继续了也可以直接说“退出”。"

        if active_task.flow_id == "complaint_request_submission":
            return "我们现在还在处理工单投诉。你可以继续补充投诉原因，或者直接回复“确认”提交。"

        return None

    def _build_slot_followup_message(
        self,
        state: DialogueState,
        slot_name: str | None,
    ) -> str | None:
        """
        功能：针对当前正在收集的槽位生成更具体的补槽提示。

        输入：
        - state: 当前运行时状态。
        - slot_name: 当前系统收集任务期待的槽位名，可为空。

        输出：
        - str | None: 命中槽位时返回对应提示，否则返回 None。

        调用情况：
        - `_build_active_task_followup_message()`

        副作用：
        - 无。
        """
        if slot_name == "urge_reason":
            return "我们现在在处理工单催办。请直接告诉我催办原因；如果你只是想尽快处理，也可以直接回复“希望尽快处理”。"

        if slot_name == "complaint_reason":
            return "我们现在在处理工单投诉。请直接说一下投诉或异议原因，我收到后继续帮你提交。"

        if slot_name == "complaint_confirm":
            return "我们现在在确认是否提交投诉。请直接回复“确认”继续提交；如果先不提交，可以回复“取消”。"

        if slot_name == "work_order_id":
            if self._get_focused_object_type(state) == "work_order":
                return "我已经拿到这条工单了。你可以直接继续说你的诉求，我来接着处理。"
            return "我们现在还缺工单信息。请告诉我工单号，或者先从右侧选中对应工单。"

        if slot_name == "service_item_id":
            if self._get_focused_object_type(state) == "service_item":
                return "我已经拿到这个服务项目了。你可以直接继续说你想了解或办理什么，我来接着处理。"
            return "我们现在还缺服务项目信息。请告诉我服务项目编号，或者先从右侧选中对应项目。"

        return None

    def _build_focused_object_guidance(self, state: DialogueState) -> str | None:
        """
        功能：当当前轮次仍围绕某个对象时，提醒用户把意图落到明确动作上。

        输入：
        - state: 当前运行时状态。

        输出：
        - str | None: 面向当前对象的引导话术；无对象时返回 None。

        调用情况：
        - `_build_missing_task_commands_message()`
        - `_build_invalid_task_commands_message()`

        副作用：
        - 无。
        """
        object_type = self._get_focused_object_type(state)
        if object_type == "work_order":
            return "你现在是在围绕这条工单继续说。你可以明确告诉我是要查状态、看进度、提交催办，还是发起投诉。"

        if object_type == "service_item":
            return "你现在是在围绕这个服务项目继续说。你可以明确告诉我是想了解收费、办理方式、服务说明，还是当前可预约状态。"

        return None

    def _build_missing_track_message(self, state: DialogueState) -> str | None:
        """
        功能：在对象上下文还在时，为“缺轨道”场景提供更贴边的提醒。

        输入：
        - state: 当前运行时状态。

        输出：
        - str | None: 命中对象上下文时返回提示，否则返回 None。

        调用情况：
        - `_build_missing_track_clarify_message()`

        副作用：
        - 无。
        """
        object_type = self._get_focused_object_type(state)
        if object_type == "work_order":
            return "你现在是在围绕这条工单继续说。要是想了解状态、进度或费用，可以直接接着问；要是想继续处理，也可以直接说催办或投诉。"

        if object_type == "service_item":
            return "你现在是在围绕这个服务项目继续说。要是想了解收费、办理方式或服务说明，可以直接接着问；要是想退出当前话题，也可以直接说。"

        return None

    @staticmethod
    def _get_focused_object_type(state: DialogueState) -> str | None:
        """
        功能：读取当前 focused object 的类型。

        输入：
        - state: 当前运行时状态。

        输出：
        - str | None: focused object.type；无对象时返回 None。

        调用情况：
        - 多个澄清分支复用。

        副作用：
        - 无。
        """
        focused_object = state.focused_object
        if focused_object is None:
            return None
        return focused_object.type
