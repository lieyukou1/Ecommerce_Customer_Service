# 05-Task轨道与Flow编排

## 这册看什么

这一册只看 task 轨：

1. task 轨从命令到流程推进的理想结构
2. 当前本地已经落地了哪些 flow 模型
3. 对象消息怎么转成 `SetSlotsCommand`

## 图 1：Task 轨总流程图

```mermaid
flowchart LR
    TurnPlan["TurnPlan.task.commands"] --> Handler["TaskHandler.handle() [占位]"]
    Handler --> Processor["CommandProcessor [预留]"]
    Processor --> State["DialogueState.active_task / paused_tasks"]
    State --> Executor["FlowExecutor [预留]"]
    Executor --> Runner["ActionRunner [预留]"]
    Runner --> Output["BotMessage[]"]
```

## 图 2：Flow 数据模型类图

```mermaid
classDiagram
    class FlowSlot {
      +name: str
      +type: str
      +label: str
      +description: str
    }

    class Flow {
      +id: str
      +name: str | None
      +description: str
      +steps: list[FlowStep]
      +slots: list[FlowSlot]
      +start_step(): StartedFlowStep | None
      +get_step_by_id(step_id: str): FlowStep | None
    }

    class FlowList {
      +flows: list[Flow]
      +slots: dict[str, FlowSlot]
      +get_flow_by_id(flow_id: str): Flow | None
    }

    FlowList --> Flow
    FlowList --> FlowSlot
    Flow --> FlowStep
    Flow --> FlowSlot
```

## 图 3：Step / Link 关系图

```mermaid
classDiagram
    class FlowStep {
      +id: str
      +type: FlowStepType
      +next: list[FlowStepLink]
      +description: str
      +from_dict(step_data: dict[str, Any]): FlowStep
      +base_load_field(base_data: dict[str, Any]): dict[str, Any]
    }

    class StartedFlowStep
    class ActionFlowStep {
      +action: str
      +args: dict[str, Any] | str
    }
    class CollectedFlowStep {
      +slot_name: str
      +response: ResponseDefinition
      +validate: SlotValidation | None
    }
    class EndFlowStep

    class FlowStepLink
    class StaticLink {
      +target: str
    }
    class ConditionalLink {
      +condition: str
      +target: str
    }
    class FallbackLink {
      +target: str
    }

    class ResponseDefinition {
      +text: str
      +mode: str
      +prompt: str | None
    }

    class SlotValidation {
      +condition: str
      +failure_response: ResponseDefinition | None
    }

    FlowStep <|-- StartedFlowStep
    FlowStep <|-- ActionFlowStep
    FlowStep <|-- CollectedFlowStep
    FlowStep <|-- EndFlowStep

    FlowStep --> FlowStepLink
    FlowStepLink <|-- StaticLink
    FlowStepLink <|-- ConditionalLink
    FlowStepLink <|-- FallbackLink
    CollectedFlowStep --> ResponseDefinition
    CollectedFlowStep --> SlotValidation
    SlotValidation --> ResponseDefinition
```

## 图 4：`Command` 体系类图

```mermaid
classDiagram
    class Command {
      +command: str
      +from_dict(data: dict[str, Any]): Command
    }

    class StartFlowCommand {
      +flow: str
    }

    class SetSlotsCommand {
      +slots: dict[str, Any]
    }

    class CancelFlowCommand

    class ResumeFlowCommand {
      +flow: str | None
    }

    Command <|-- StartFlowCommand
    Command <|-- SetSlotsCommand
    Command <|-- CancelFlowCommand
    Command <|-- ResumeFlowCommand
```

## 图 5：对象消息生成 `SetSlotsCommand` 的流程图

```mermaid
flowchart TD
    Obj["FocusedObject"] --> Type{"object.type"}

    Type -->|work_order| Work["检查 work_order_id 槽位"]
    Type -->|service_item| Item["检查 service_item_id 槽位"]

    Work --> WorkNeed{"当前 flow 存在未填 work_order_id?"}
    Item --> ItemNeed{"当前 flow 存在未填 service_item_id?"}

    WorkNeed -->|是| WorkCmd["SetSlotsCommand(command='set_slots', slots={'work_order_id': object.id})"]
    WorkNeed -->|否| Empty1["[]"]

    ItemNeed -->|是| ItemCmd["SetSlotsCommand(command='set_slots', slots={'service_item_id': object.id})"]
    ItemNeed -->|否| Empty2["[]"]
```

## 配置与边界表

| 位置 | 当前状态 | 说明 |
| --- | --- | --- |
| `task/handler.py` | `[占位]` | 当前只有入口壳 |
| `task/flow/loader.py` | `[已实现]` | 已能从 YAML 加载 flow |
| `task/flow/flows.py` | `[已实现]` | Flow / FlowList / FlowSlot 已齐 |
| `task/flow/steps.py` | `[已实现]` | Step / Link / Response / Validation 已齐 |
| `flow_config/user_flows.yml` | `[已实现]` | 已切成物业语义 |
| `flow_config/system_flows.yml` | `[已实现]` | 系统流程定义存在 |
| `CommandProcessor` | `[预留]` | 老师架构下一步 |
| `FlowExecutor` | `[预留]` | 老师架构流程推进器 |
| `ActionRunner` | `[预留]` | 老师架构动作执行器 |

## 一句话结论

task 轨最完整的是“数据模型层”，最缺的是“命令执行层”和“流程推进层”。
