from pathlib import Path

from atguigu.chitchat.handler import ChitchatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.turn_validator import TurnPlanValidator
from atguigu.task.action.builder import build_action_runner
from atguigu.task.action.runner import ActionRunner
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.flow.executor import FlowExecutor
from atguigu.task.flow.loader import FlowLoader
from atguigu.task.handler import TaskHandler

# 真正加载YAML
PROJECT_DIR = Path(__file__).resolve().parents[2]
FLOW_CONFIG_DIR = PROJECT_DIR / "flow_config"
FLOW_CONFIG_FILES = ["system_flows.yml", "user_flows.yml"]


def build_dialogue_engine():
    """

    """
    flows = FlowLoader().load_many([FLOW_CONFIG_DIR / file_name for file_name in FLOW_CONFIG_FILES])

    return DialogueEngine(
        turn_planner=TurnPlanner(),
        turn_validator=TurnPlanValidator(),
        task_handler=TaskHandler(
            flows=flows,
            processor=CommandProcessor(),
            action_runner=build_action_runner(),
            flow_executor=FlowExecutor(),
        ),
        knowledge_handler=KnowledgeHandler(knowledge_intents=KNOWLEDGE_INTENTS),
        chit_chat_handler=ChitchatHandler(),
        clarify_responder=ClarifyResponder(),
    )
