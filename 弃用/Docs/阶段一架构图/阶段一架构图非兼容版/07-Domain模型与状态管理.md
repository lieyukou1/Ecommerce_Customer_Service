# 07-Domain模型与状态管理

## 这册看什么

这一册是状态底盘：

1. `messages.py` 定义了哪些消息对象
2. `contexts.py` 定义了哪些任务 / 系统上下文
3. `DialogueState` 聚合根如何组织会话、任务、焦点对象和 pending turn

## 图 1：`messages.py` 类图

```mermaid
classDiagram
    class FocusedObject {
      +id: str
      +type: str
      +title: str
      +attributes: dict[str, Any]
      +to_dict(): dict[str, Any]
      +from_dict(data: dict[str, Any]): FocusedObject
    }

    class UserMessage {
      +resident_id: str
      +message_id: str
      +type: MessageType
      +text: str | None
      +object: FocusedObject | None
      +to_dict(): dict[str, Any]
      +from_dict(data: dict[str, Any]): UserMessage
    }

    class BotMessage {
      +text: str | None
      +object: FocusedObject | None
      +to_dict(): dict[str, Any]
      +from_dict(data: dict[str, Any]): BotMessage
    }

    class ProcessResult {
      +resident_id: str
      +message_id: str
      +messages: list[BotMessage]
    }

    UserMessage --> FocusedObject
    BotMessage --> FocusedObject
    ProcessResult --> BotMessage
```

## 图 2：`contexts.py` 类图

```mermaid
classDiagram
    class TaskContext {
      +flow_id: str
      +step_id: str | None
      +slots: dict[str, Any]
      +to_dict(): dict[str, Any]
      +from_dict(data: dict[str, Any]): TaskContext
    }

    class SystemContext {
      +flow_id: str
      +step_id: str | None
      +to_dict(): dict[str, Any]
      +from_dict(data: dict[str, Any]): SystemContext
    }

    class StartedSystemContext {
      +started_flow_id: str
      +started_flow_name: str
    }

    class InterruptedSystemContext {
      +interrupted_flow_id: str
      +interrupted_flow_name: str
      +started_flow_id: str
      +started_flow_name: str
    }

    class CanceledSystemContext {
      +canceled_flow_id: str
      +canceled_flow_name: str
    }

    class ResumedSystemContext {
      +resumed_flow_id: str
      +resumed_flow_name: str
    }

    class CollectedSystemContext {
      +slot_name: str
      +response: dict[str, Any]
    }

    SystemContext <|-- StartedSystemContext
    SystemContext <|-- InterruptedSystemContext
    SystemContext <|-- CanceledSystemContext
    SystemContext <|-- ResumedSystemContext
    SystemContext <|-- CollectedSystemContext
```

## 图 3：`state.py` 聚合根类图

```mermaid
classDiagram
    class Turn {
      +turn_id: str
      +user_message: UserMessage
      +bot_messages: list[BotMessage]
      +to_dict(): dict[str, Any]
      +from_dict(data: dict[str, Any]): Turn
    }

    class Session {
      +session_id: str
      +started_at: float
      +last_activity_at: float
      +closed_at: float | None
      +turns: list[Turn]
      +to_dict(): dict[str, Any]
      +from_dict(data: dict[str, Any]): Session
    }

    class DialogueState {
      +resident_id: str
      +active_task: TaskContext | None
      +paused_tasks: list[TaskContext]
      +active_system_task: SystemContext | None
      +focused_object: FocusedObject | None
      +sessions: list[Session]
      +current_session_id: str | None
      +pending_turn: Turn | None
      +to_dict(): dict[str, Any]
      +from_dict(data: dict[str, Any]): DialogueState
      +start_active_task(task_context: TaskContext)
      +end_active_task()
      +cancel_active_task()
      +interrupt_active_task()
      +resume_task(flow_id: str | None)
      +start_active_system_task(system_context: SystemContext)
      +end_active_system_task()
      +current_active_task()
      +set_slots(slots: dict[str, Any])
      +remove_slot(slot_name: str)
      +start_session()
      +current_session()
      +close_session()
      +reset_running_state_for_new_session()
      +begin_turn(message: UserMessage)
      +commit_turn()
      +set_focused_object(focused_object: FocusedObject)
    }

    DialogueState --> TaskContext
    DialogueState --> SystemContext
    DialogueState --> FocusedObject
    DialogueState --> Session
    DialogueState --> Turn
    Session --> Turn
    Turn --> UserMessage
    Turn --> BotMessage
```

## 图 4：`DialogueState` 状态关系图

```mermaid
flowchart TB
    DS["DialogueState"] --> AT["active_task"]
    DS --> PT["paused_tasks"]
    DS --> AST["active_system_task"]
    DS --> FO["focused_object"]
    DS --> SS["sessions"]
    DS --> CS["current_session_id"]
    DS --> P["pending_turn"]
```

## 图 5：会话 / 轮次 / 任务栈状态图

```mermaid
stateDiagram-v2
    [*] --> NoSession
    NoSession --> SessionActive: start_session()
    SessionActive --> TurnPending: begin_turn()
    TurnPending --> SessionActive: commit_turn()
    SessionActive --> SessionClosed: close_session()
    SessionClosed --> SessionActive: start_session()

    --

    [*] --> NoTask
    NoTask --> ActiveTask: start_active_task()
    ActiveTask --> Interrupted: interrupt_active_task()
    Interrupted --> ActiveTask: resume_task()
    ActiveTask --> NoTask: end_active_task() / cancel_active_task()
```

## 图 6：pending turn 提交流程图

```mermaid
flowchart LR
    begin["begin_turn(user_message)"] --> pending["pending_turn = Turn(...)"]
    pending --> write["engine 写 bot_messages"]
    write --> commit["commit_turn()"]
    commit --> append["current_session().turns.append(pending_turn)"]
    append --> clear["pending_turn = None"]
```

## 一句话结论

`DialogueState` 是整个后端的运行时聚合根，engine 的所有决策最终都体现在这份内存状态对象的演化上。
