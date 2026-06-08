from atguigu.domain.messages import MessageType, UserMessage
from atguigu.domain.state import DialogueState
from atguigu.engine.focus.catalog import FocusedObjectCatalog
from atguigu.engine.focus.slot_handoff import ObjectSlotHandoff
from atguigu.engine.focus.text_switch import FocusedObjectTextSwitch
from atguigu.task.command.models import Command
from atguigu.task.flow.flows import FlowList


class FocusedObjectResolver:
    """
    功能：统一承接 focused object 的文本切换与对象消息承接。
    """

    def __init__(self) -> None:
        """
        功能：构造 focused object 解析器。

        输入：
        - 无。

        输出：
        - 无返回值；初始化候选目录、文本切换器和对象承接器。

        调用情况：
        - `DialogueEngine.__init__()`

        副作用：
        - 无。
        """
        self._catalog = FocusedObjectCatalog()
        self._text_switch = FocusedObjectTextSwitch()
        self._slot_handoff = ObjectSlotHandoff()

    async def try_switch_focused_object_from_text(self, dialogue_state: DialogueState) -> None:
        """
        功能：尝试根据文本内容把当前 focused object 切换到另一个候选对象。

        输入：
        - dialogue_state: 当前运行时状态。

        输出：
        - 无返回值。

        调用情况：
        - `TextTurnHandler.handle()` 在 planner 前调用。

        副作用：
        - 命中唯一候选对象时，会更新 `dialogue_state.focused_object`。
        """
        pending_turn = dialogue_state.pending_turn
        if pending_turn is None or pending_turn.user_message.type is not MessageType.TEXT:
            return

        # 正在执行任务或系统收集流程时，不再从文本里做对象切换，避免上下文串味。
        if dialogue_state.active_task is not None or dialogue_state.active_system_task is not None:
            return

        candidates = await self._catalog.load_resident_candidates(dialogue_state.resident_id)
        matched_object = self._text_switch.match_candidate_from_text(
            text=pending_turn.user_message.text,
            candidates=candidates,
            current_object=dialogue_state.focused_object,
        )
        if matched_object is None:
            return

        dialogue_state.set_focused_object(focused_object=matched_object)

    def resolve_object_commands(
        self,
        *,
        user_message: UserMessage,
        dialogue_state: DialogueState,
        flows: FlowList,
    ) -> list[Command]:
        """
        功能：尝试把对象消息承接成可执行 command。

        输入：
        - user_message: 当前对象消息。
        - dialogue_state: 当前运行时状态。
        - flows: 当前可用 flow 列表。

        输出：
        - list[Command]: 由对象消息导出的命令列表；无法承接时返回空列表。

        调用情况：
        - `ObjectTurnHandler._build_object_context()`

        副作用：
        - 无；仅做对象到命令的映射判断。
        """
        return self._slot_handoff.resolve_commands(
            user_message=user_message,
            dialogue_state=dialogue_state,
            flows=flows,
        )
