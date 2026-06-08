import json
from dataclasses import asdict
from typing import Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from atguigu.infrastructure.llm import llm
from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.turn_plan import TurnPlan
from atguigu.prompt.history_builder import HistoryBuilder
from atguigu.prompt.loader import load_prompt
from atguigu.task.flow.flows import FlowList


class TurnPlanner:
    """
    意图分析器
    作用：根据任务自然语言 调用LLM 分析轨道类型
    """

    async def predict(self,
                      dialogue_state: DialogueState,
                      flows: FlowList,
                      intents:Dict[str, KnowledgeIntent]) -> TurnPlan:
        """

        """
        # 1.构建提示词
        prompt = self._build_input_prompt(dialogue_state, flows, intents)

        # 2.调用llm
        turn_plan = await  self._predict_from_inputs_prompt(prompt)

        return turn_plan

    def _build_input_prompt(self,
                            dialogue_state: DialogueState,
                            flows_list: FlowList,
                            intents: Dict[str, KnowledgeIntent]) -> Dict[str, Any]:
        """

        """
        # 1.user_message
        user_message = HistoryBuilder._render_user_message(user_message=dialogue_state.pending_turn.user_message)

        # 2.current_conversation
        current_conversation = HistoryBuilder.build(turns=dialogue_state.current_session().turns[-10:])

        # 3.active_task_json
        active_task_json = json.dumps(
            dialogue_state.active_task.to_dict(), ensure_ascii=False
        ) if dialogue_state.active_task is not None else None

        # 4.interrupted_tasks_json
        interrupted_tasks_json = json.dumps(
            [paused_task.to_dict() for paused_task in dialogue_state.paused_tasks], ensure_ascii=False
        )

        # 5.focused_object_json
        focused_object_json = json.dumps(
            dialogue_state.focused_object.to_dict(), ensure_ascii=False
        ) if dialogue_state.focused_object is not None else None

        # 6.available_flows_json
        available_flows_json = json.dumps(
            {
                "flows": [{k: v for k, v in asdict(flow).items() if k != "steps"} for flow in flows_list.flows]
            }, ensure_ascii=False
        )

        # 7.knowledge_intents_json
        knowledge_intents_json = json.dumps(
            [{"id": intent.id, "description": intent.description} for intent in intents.values()],
            ensure_ascii=False
        )

        return {
            "user_message": user_message,
            "current_conversation": current_conversation,
            "active_task_json": active_task_json,
            "interrupted_tasks_json": interrupted_tasks_json,
            "focused_object_json": focused_object_json,
            "available_flows_json": available_flows_json,
            "knowledge_intents_json": knowledge_intents_json,
        }

    async def _predict_from_inputs_prompt(self, prompt) -> TurnPlan:
        """
        1. 加载提示词模板
        2. 格式化模版
        3. 调用模型
        """
        prompt_template = load_prompt("turn_plan")

        prompt_template = PromptTemplate.from_template(prompt_template, template_format='jinja2')

        chain = prompt_template | llm | JsonOutputParser()

        llm_response_dict: Dict[str, Any] = await chain.ainvoke(prompt)

        return TurnPlan.from_dict(llm_response_dict)
