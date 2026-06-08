from dataclasses import dataclass

from atguigu.clarify.responder import ClarifyResponder
from atguigu.domain.contexts import TaskContext
from atguigu.domain.messages import BotMessage, FocusedObject, UserMessage
from atguigu.domain.state import DialogueState
from atguigu.engine.focus import FocusedObjectResolver
from atguigu.engine.state_decision import StateDecisionEngine
from atguigu.engine.track_execution.task_command_executor import TaskCommandExecutor
from atguigu.plan.turn_plan import ClarifyContext
from atguigu.task.command.models import Command
from atguigu.task.flow.flows import FlowList


@dataclass(slots=True)
class _ObjectTurnContext:
    user_object: FocusedObject
    previous_focused_object: FocusedObject | None
    active_task_before: TaskContext | None
    commands: list[Command]


class ObjectTurnHandler:
    def __init__(
        self,
        *,
        task_executor: TaskCommandExecutor,
        clarify_responder: ClarifyResponder,
        state_decision: StateDecisionEngine,
        focus_resolver: FocusedObjectResolver,
    ) -> None:
        """
        功能：构造对象消息执行入口，负责对象承接、对象切换和对象到 task 的衔接。

        输入：
        - task_executor: 负责执行对象触发出的 task 命令。
        - clarify_responder: 当对象缺少意图时输出澄清回复。
        - state_decision: 负责路由与状态迁移。
        - focus_resolver: 负责把对象消息解析成 slot handoff 命令。

        输出：
        - 无返回值；初始化对象执行入口依赖。

        调用情况：
        - 由 `build_track_execution_runtime()` 装配，供 `DialogueEngine._route_turn()` 的对象分支调用。

        副作用：
        - 无；只保存依赖引用。
        """
        self.task_executor = task_executor
        self.clarify_responder = clarify_responder
        self.state_decision = state_decision
        self.focus_resolver = focus_resolver

    async def handle(
        self,
        dialogue_state: DialogueState,
        *,
        user_message: UserMessage,
        flows: FlowList,
    ) -> list[BotMessage]:
        """
        功能：处理对象消息，决定是直接承接 task、继续当前 task，还是先澄清用户意图。

        输入：
        - dialogue_state: 当前住户运行时状态。
        - user_message: 携带对象信息的领域层消息。
        - flows: 当前可用的任务流配置集合。

        输出：
        - list[BotMessage]: 对象消息生成的回复列表。

        调用情况：
        - 由 `DialogueEngine._route_turn()` 在对象消息分支调用。

        副作用：
        - 会修改 focused object、runtime state，以及可能触发 task 执行。
        """
        object_context = self._build_object_context(
            dialogue_state,
            user_message=user_message,
            flows=flows,
        )
        if object_context is None:
            # 没拿到有效对象时，直接退回“对象有了但意图不明确”的澄清路径。
            return await self._respond_object_requires_intent(dialogue_state, None)
        return await self._execute_object_context(dialogue_state, object_context)

    def _build_object_context(
        self,
        dialogue_state: DialogueState,
        *,
        user_message: UserMessage,
        flows: FlowList,
    ) -> _ObjectTurnContext | None:
        """
        功能：从对象消息中提取对象上下文，并尝试解析可执行命令。

        输入：
        - dialogue_state: 当前运行时状态。
        - user_message: 对象消息。
        - flows: 当前可用任务流配置集合。

        输出：
        - _ObjectTurnContext | None: 能继续执行时返回对象上下文；没有对象时返回 None。

        调用情况：
        - 由 `handle()` 调用。

        副作用：
        - 会先把 `dialogue_state.focused_object` 更新为本次对象。
        """
        user_object = user_message.object
        if user_object is None:
            return None

        previous_focused_object = dialogue_state.focused_object
        active_task_before = dialogue_state.active_task
        # 对象消息一旦进入，就先把当前焦点切到该对象，供后续意图解析和 task 承接使用。
        dialogue_state.set_focused_object(focused_object=user_object)
        # focus_resolver 会尝试把“点击了对象”翻译成可执行命令，例如补槽或触发只读 flow。
        commands = self.focus_resolver.resolve_object_commands(
            user_message=user_message,
            dialogue_state=dialogue_state,
            flows=flows,
        )
        return _ObjectTurnContext(
            user_object=user_object,
            previous_focused_object=previous_focused_object,
            active_task_before=active_task_before,
            commands=commands,
        )

    async def _execute_object_context(
        self,
        dialogue_state: DialogueState,
        object_context: _ObjectTurnContext,
    ) -> list[BotMessage]:
        """
        功能：按对象上下文选择对象消息的实际执行路径。

        输入：
        - dialogue_state: 当前运行时状态。
        - object_context: 已构造好的对象上下文。

        输出：
        - list[BotMessage]: 对象消息的回复列表。

        调用情况：
        - 由 `handle()` 在成功构建对象上下文后调用。

        副作用：
        - 可能重置 runtime state、继续当前 task，或进入澄清分支。
        """
        if self._is_object_switch_during_active_task(
            active_task_before=object_context.active_task_before,
            previous_focused_object=object_context.previous_focused_object,
            next_object=object_context.user_object,
        ):
            # 正在办任务时切到另一个对象，先清理旧运行时，再要求用户明确新对象意图。
            return await self._handle_object_switch_during_active_task(
                dialogue_state,
                object_context,
            )

        if object_context.commands:
            # 能直接从对象解析出命令时，优先走 slot handoff / 只读 task 执行。
            return await self._handoff_object_slots(dialogue_state, object_context)

        if dialogue_state.active_task is not None:
            # 还在 task 上下文里，但本次对象没有直接命令时，继续沿当前 task 执行。
            return await self._continue_active_task_with_object(dialogue_state, object_context)

        # 只有对象，没有明确意图时，统一回到澄清轨。
        return await self._respond_object_requires_intent(dialogue_state, object_context.user_object)

    async def _handle_object_switch_during_active_task(
        self,
        dialogue_state: DialogueState,
        object_context: _ObjectTurnContext,
    ) -> list[BotMessage]:
        """
        功能：处理“任务进行中切换对象”的场景。

        输入：
        - dialogue_state: 当前运行时状态。
        - object_context: 记录了切换前后对象与旧 task 的上下文。

        输出：
        - list[BotMessage]: 切换后要求用户明确新对象意图的澄清回复。

        调用情况：
        - 由 `_execute_object_context()` 在检测到任务中的对象切换时调用。

        副作用：
        - 会重置 runtime state，并把 focused object 设置为新对象。
        """
        previous_object = object_context.previous_focused_object
        user_object = object_context.user_object
        switch_reason = f"{previous_object.type}:{previous_object.id}->{user_object.type}:{user_object.id}"
        # 旧任务上下文与新对象无法安全混用，先整体退出旧 runtime，再切入新对象。
        dialogue_state.reset_runtime_state(
            event="object_switch_during_task_context",
            reason=switch_reason,
        )
        dialogue_state.set_focused_object(focused_object=user_object)
        return await self._respond_object_requires_intent(dialogue_state, user_object)

    async def _handoff_object_slots(
        self,
        dialogue_state: DialogueState,
        object_context: _ObjectTurnContext,
    ) -> list[BotMessage]:
        """
        功能：把对象解析出的命令交给 task 执行包装器。

        输入：
        - dialogue_state: 当前运行时状态。
        - object_context: 当前对象上下文，包含待执行命令。

        输出：
        - list[BotMessage]: task 执行后的回复列表。

        调用情况：
        - 由 `_execute_object_context()` 在对象能直接解析出命令时调用。

        副作用：
        - 会触发 task route 决策、task 执行和 task outcome 回写。
        """
        object_reason = self.state_decision.describe_focused_object(object_context.user_object)
        return await self.task_executor.execute(
            dialogue_state,
            commands=object_context.commands,
            route_event="object_slot_handoff",
            route_reason=object_reason,
            source_event="object_slot_handoff",
            default_reason=object_reason,
        )

    async def _continue_active_task_with_object(
        self,
        dialogue_state: DialogueState,
        object_context: _ObjectTurnContext,
    ) -> list[BotMessage]:
        """
        功能：在已有 active task 里继续处理当前对象消息。

        输入：
        - dialogue_state: 当前运行时状态。
        - object_context: 当前对象上下文。

        输出：
        - list[BotMessage]: 当前 task 继续执行后的回复列表。

        调用情况：
        - 由 `_execute_object_context()` 在仍存在 active task 时调用。

        副作用：
        - 会沿当前 task 上下文继续执行，并更新 task outcome。
        """
        object_reason = self.state_decision.describe_focused_object(object_context.user_object)
        return await self.task_executor.execute(
            dialogue_state,
            commands=object_context.commands,
            route_event="object_message_during_active_task",
            route_reason=object_reason,
            source_event="object_message_active_task",
            default_reason=object_reason,
        )

    async def _respond_object_requires_intent(
        self,
        dialogue_state: DialogueState,
        user_object: FocusedObject | None,
    ) -> list[BotMessage]:
        """
        功能：当对象已选中但用户意图不明确时，统一返回对象意图澄清。

        输入：
        - dialogue_state: 当前运行时状态。
        - user_object: 本次对象消息对应的对象，可为空。

        输出：
        - list[BotMessage]: 对象意图澄清回复。

        调用情况：
        - 由 `handle()`、`_handle_object_switch_during_active_task()`、`_execute_object_context()` 调用。

        副作用：
        - 会把 route 和记为 clarify，并把 conversation_state 切到澄清态。
        """
        self.state_decision.apply_clarify(
            dialogue_state,
            event="object_requires_intent",
            clarify_context=ClarifyContext.for_object_intent(),
            reason=self.state_decision.describe_focused_object(user_object),
        )
        return await self.clarify_responder.respond(
            state=dialogue_state,
            clarify_context=ClarifyContext.for_object_intent(),
        )

    @staticmethod
    def _is_object_switch_during_active_task(
        *,
        active_task_before,
        previous_focused_object: FocusedObject | None,
        next_object: FocusedObject,
    ) -> bool:
        """
        功能：判断当前对象消息是否意味着“任务进行中切换到了另一个对象”。

        输入：
        - active_task_before: 对象消息处理前的 active task。
        - previous_focused_object: 切换前的 focused object。
        - next_object: 当前对象消息携带的新对象。

        输出：
        - bool: 若属于任务中的对象切换则返回 True。

        调用情况：
        - 由 `_execute_object_context()` 调用。

        副作用：
        - 无。
        """
        return (
            active_task_before is not None
            and previous_focused_object is not None
            and (
                previous_focused_object.type != next_object.type
                or previous_focused_object.id != next_object.id
            )
        )
