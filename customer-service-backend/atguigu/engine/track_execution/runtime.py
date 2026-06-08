from dataclasses import dataclass

from atguigu.chitchat.handler import ChitchatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.engine.focus import FocusedObjectResolver
from atguigu.engine.state_decision import StateDecisionEngine
from atguigu.engine.track_execution.object_turn_handler import ObjectTurnHandler
from atguigu.engine.track_execution.task_command_executor import TaskCommandExecutor
from atguigu.engine.track_execution.text_turn_handler import TextTurnHandler
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.protocol_gate import TurnProtocolGate
from atguigu.task.handler import TaskHandler


@dataclass(slots=True)
class TrackExecutionRuntime:
    text_turn_handler: TextTurnHandler
    object_turn_handler: ObjectTurnHandler


def build_track_execution_runtime(
    *,
    turn_planner: TurnPlanner,
    turn_protocol_gate: TurnProtocolGate,
    task_handler: TaskHandler,
    knowledge_handler: KnowledgeHandler,
    chit_chat_handler: ChitchatHandler,
    clarify_responder: ClarifyResponder,
    state_decision: StateDecisionEngine,
    focus_resolver: FocusedObjectResolver,
) -> TrackExecutionRuntime:
    """
    功能：组装 track execution 层的运行时对象。

    输入：
    - turn_planner: planner 层入口。
    - turn_protocol_gate: 协议闸门入口。
    - task_handler: task 执行器。
    - knowledge_handler: knowledge 轨处理器。
    - chit_chat_handler: chitchat 轨处理器。
    - clarify_responder: clarify 轨处理器。
    - state_decision: 状态决策引擎。
    - focus_resolver: 对象焦点解析器。

    输出：
    - TrackExecutionRuntime: 聚合好的文本执行入口和对象执行入口。

    调用情况：
    - 由 `DialogueEngine.__init__()` 调用。

    副作用：
    - 无外部副作用；只是统一构造本层依赖对象。
    """
    # task executor 被文本轨和对象轨共用，确保 task 执行前后状态处理口径一致。
    task_executor = TaskCommandExecutor(
        task_handler=task_handler,
        state_decision=state_decision,
    )
    return TrackExecutionRuntime(
        text_turn_handler=TextTurnHandler(
            turn_planner=turn_planner,
            turn_protocol_gate=turn_protocol_gate,
            task_executor=task_executor,
            knowledge_handler=knowledge_handler,
            chit_chat_handler=chit_chat_handler,
            clarify_responder=clarify_responder,
            state_decision=state_decision,
            focus_resolver=focus_resolver,
        ),
        object_turn_handler=ObjectTurnHandler(
            task_executor=task_executor,
            clarify_responder=clarify_responder,
            state_decision=state_decision,
            focus_resolver=focus_resolver,
        ),
    )
