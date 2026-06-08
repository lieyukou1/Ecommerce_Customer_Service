from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Command:
    command: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Command":
        """
        功能：把模型输出的命令字典反序列化成具体 Command 子类。

        输入：
        - data: 至少包含 `command` 字段的字典。

        输出：
        - Command: 命中已注册命令类型时返回对应子类，否则返回 `command="unknown"` 的兜底命令。

        调用情况：
        - 由 `TaskTurnPlan.from_dict()` 调用。

        副作用：
        - 无。
        """
        clz = COMMAND_NAME_TO_CLASS.get(data.get("command"))
        if clz is not None:
            return clz(**data)
        return Command(command="unknown")


@dataclass
class StartFlowCommand(Command):
    # planner 指定要启动的业务 flow_id。
    flow: str


@dataclass
class SetSlotsCommand(Command):
    # planner 或对象承接逻辑给出的槽位字典。
    slots: Dict[str, Any]


@dataclass
class CancelFlowCommand(Command):
    # 当前仅支持取消当前上下文中的 flow。
    pass


@dataclass
class ResumeFlowCommand(Command):
    # 指定要恢复的 flow_id；为空时表示恢复最近被打断的任务。
    flow: str | None = None


COMMAND_NAME_TO_CLASS = {
    "start_flow": StartFlowCommand,
    "set_slots": SetSlotsCommand,
    "cancel_flow": CancelFlowCommand,
    "resume_flow": ResumeFlowCommand,
}
