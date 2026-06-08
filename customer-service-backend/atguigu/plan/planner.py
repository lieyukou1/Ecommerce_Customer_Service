import json
from dataclasses import asdict
from typing import Any, Dict

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from atguigu.domain.state import DialogueState
from atguigu.infrastructure.llm import llm
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.turn_plan import TurnPlan
from atguigu.prompt.history_builder import HistoryBuilder
from atguigu.prompt.loader import load_prompt
from atguigu.task.flow.flows import FlowList


class TurnPlanner:
    """
    功能：基于当前对话状态、可用 flow 和知识意图，调用 LLM 生成结构化 TurnPlan。
    """

    async def predict(
        self,
        dialogue_state: DialogueState,
        flows: FlowList,
        intents: Dict[str, KnowledgeIntent],
    ) -> TurnPlan:
        """
        功能：为当前待处理消息生成结构化 TurnPlan。

        输入：
        - dialogue_state: 当前住户的完整运行时状态，要求其中已存在 pending_turn。
        - flows: 当前可用的任务流配置集合。
        - intents: 当前可用的知识意图注册表。

        输出：
        - TurnPlan: LLM 输出并反序列化后的结构化轮次计划。

        调用情况：
        - 由 `TextTurnHandler.handle()` 调用，是文本消息进入 planner 层的唯一入口。

        副作用：
        - 会调用外部 LLM，但不直接修改 DialogueState。
        """
        # 先把当前轮次需要给模型看的上下文全部整理成 prompt 入参。
        prompt = self._build_input_prompt(dialogue_state, flows, intents)
        # 调用 LLM 并把 JSON 结果还原成 TurnPlan。
        turn_plan = await self._predict_from_inputs_prompt(prompt)
        return turn_plan

    def _build_input_prompt(
        self,
        dialogue_state: DialogueState,
        flows_list: FlowList,
        intents: Dict[str, KnowledgeIntent],
    ) -> Dict[str, Any]:
        """
        功能：构造 turn_plan 提示词模板所需的完整输入字典。

        输入：
        - dialogue_state: 当前运行时状态。
        - flows_list: 当前可用 flow 列表。
        - intents: 当前可用知识意图注册表。

        输出：
        - Dict[str, Any]: 传入 PromptTemplate 的结构化上下文字典。

        调用情况：
        - 由 `predict()` 调用。

        副作用：
        - 无；只做序列化和上下文拼装。
        """
        return {
            "user_message": self._render_user_message(dialogue_state),
            "current_conversation": self._build_current_conversation(dialogue_state),
            "runtime_state_json": self._build_runtime_state_json(dialogue_state),
            "active_task_json": self._serialize_context(dialogue_state.active_task),
            "active_system_task_json": self._serialize_context(dialogue_state.active_system_task),
            "interrupted_tasks_json": self._build_interrupted_tasks_json(dialogue_state),
            "focused_object_json": self._serialize_context(dialogue_state.focused_object),
            "available_flows_json": self._build_available_flows_json(flows_list),
            "knowledge_intents_json": self._build_knowledge_intents_json(intents),
        }

    @staticmethod
    def _render_user_message(dialogue_state: DialogueState) -> str:
        """
        功能：把当前 pending_turn 中的用户消息渲染成模型可读文本。

        输入：
        - dialogue_state: 当前运行时状态，要求 pending_turn 已存在。

        输出：
        - str: 用户消息的文本化表示。

        调用情况：
        - 由 `_build_input_prompt()` 调用。

        副作用：
        - 无。
        """
        return HistoryBuilder._render_user_message(
            user_message=dialogue_state.pending_turn.user_message
        )

    @staticmethod
    def _build_current_conversation(dialogue_state: DialogueState) -> str:
        """
        功能：构造最近多轮对话历史文本，供模型理解当前上下文。

        输入：
        - dialogue_state: 当前运行时状态。

        输出：
        - str: 最近最多 10 个 turn 的历史文本。

        调用情况：
        - 由 `_build_input_prompt()` 调用。

        副作用：
        - 无。
        """
        return HistoryBuilder.build(turns=dialogue_state.current_session().turns[-10:])

    @staticmethod
    def _build_runtime_state_json(dialogue_state: DialogueState) -> str:
        """
        功能：提取 conversation_state、last_route 等高层运行时状态，供模型判断延续或切换。

        输入：
        - dialogue_state: 当前运行时状态。

        输出：
        - str: 仅包含高层状态字段的 JSON 字符串。

        调用情况：
        - 由 `_build_input_prompt()` 调用。

        副作用：
        - 无。
        """
        return json.dumps(
            {
                "conversation_state": dialogue_state.conversation_state,
                "last_transition": dialogue_state.last_transition.to_dict() if dialogue_state.last_transition else None,
                "last_route": dialogue_state.last_route.to_dict() if dialogue_state.last_route else None,
                "last_task_outcome": dialogue_state.last_task_outcome.to_dict() if dialogue_state.last_task_outcome else None,
            },
            ensure_ascii=False,
        )

    @staticmethod
    def _serialize_context(context) -> str | None:
        """
        功能：把 task / system task / focused object 这类上下文对象序列化成 JSON。

        输入：
        - context: 任意实现 `to_dict()` 的上下文对象，可为空。

        输出：
        - str | None: JSON 字符串；无上下文时返回 None。

        调用情况：
        - 由 `_build_input_prompt()` 调用。

        副作用：
        - 无。
        """
        if context is None:
            return None
        return json.dumps(context.to_dict(), ensure_ascii=False)

    @staticmethod
    def _build_interrupted_tasks_json(dialogue_state: DialogueState) -> str:
        """
        功能：序列化当前被打断的任务列表。

        输入：
        - dialogue_state: 当前运行时状态。

        输出：
        - str: paused_tasks 的 JSON 字符串。

        调用情况：
        - 由 `_build_input_prompt()` 调用。

        副作用：
        - 无。
        """
        return json.dumps(
            [paused_task.to_dict() for paused_task in dialogue_state.paused_tasks],
            ensure_ascii=False,
        )

    @staticmethod
    def _build_available_flows_json(flows_list: FlowList) -> str:
        """
        功能：把可用 flow 列表压缩成适合给模型看的摘要 JSON。

        输入：
        - flows_list: 当前可用的 flow 配置集合。

        输出：
        - str: 不包含 steps 细节的 flow 摘要 JSON。

        调用情况：
        - 由 `_build_input_prompt()` 调用。

        副作用：
        - 无。
        """
        return json.dumps(
            {
                "flows": [{k: v for k, v in asdict(flow).items() if k != "steps"} for flow in flows_list.flows]
            },
            ensure_ascii=False,
        )

    @staticmethod
    def _build_knowledge_intents_json(intents: Dict[str, KnowledgeIntent]) -> str:
        """
        功能：把知识意图注册表裁剪成供模型识别的最小摘要。

        输入：
        - intents: 当前可用知识意图字典。

        输出：
        - str: 仅包含意图 ID 和描述的 JSON 字符串。

        调用情况：
        - 由 `_build_input_prompt()` 调用。

        副作用：
        - 无。
        """
        return json.dumps(
            [{"id": intent.id, "description": intent.description} for intent in intents.values()],
            ensure_ascii=False,
        )

    async def _predict_from_inputs_prompt(self, prompt) -> TurnPlan:
        """
        功能：加载 turn_plan 模板，调用 LLM，并把 JSON 输出还原成 TurnPlan。

        输入：
        - prompt: 已整理好的提示词输入字典。

        输出：
        - TurnPlan: 解析后的结构化计划对象。

        调用情况：
        - 由 `predict()` 调用。

        副作用：
        - 会调用外部 LLM。
        """
        # 先加载 Jinja2 提示词模板，并转换成 LangChain PromptTemplate。
        prompt_template = load_prompt("turn_plan")
        prompt_template = PromptTemplate.from_template(prompt_template, template_format="jinja2")
        # 链路固定为：模板渲染 -> LLM 调用 -> JSON 解析。
        chain = prompt_template | llm | JsonOutputParser()
        llm_response_dict: Dict[str, Any] = await chain.ainvoke(prompt)
        return TurnPlan.from_dict(llm_response_dict)
