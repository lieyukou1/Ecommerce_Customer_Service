# 04-Engine与Infer决策链

## 这册看什么

这一册是核心册。

这里把你说的 infer 层统一表述为：**Engine + Plan/Clarify 决策链**。

它回答：

1. `DialogueEngine` 装了哪些组件
2. 文本消息和对象消息分别怎么走
3. `TurnPlanner / TurnPlanValidator / ClarifyResponder` 是怎么串起来的
4. 三轨 `TurnPlan` 长什么样

## 图 1：`DialogueEngine` 组件装配图

```mermaid
flowchart TB
    subgraph Builder["engine.builder.build_dialogue_engine()"]
        loader["FlowLoader.load_many(...)"]
        flows["FlowList"]
        planner["TurnPlanner"]
        validator["TurnPlanValidator"]
        clarify["ClarifyResponder"]
        task["TaskHandler [占位]"]
        knowledge["KnowledgeHandler [占位]"]
        chit["ChitchatHandler [占位]"]
        engine["DialogueEngine"]
    end

    loader --> flows
    flows --> task
    planner --> engine
    validator --> engine
    clarify --> engine
    task --> engine
    knowledge --> engine
    chit --> engine
```

## 图 2：文本消息处理时序图

```mermaid
sequenceDiagram
    participant Engine as DialogueEngine
    participant State as DialogueState
    participant Planner as TurnPlanner
    participant Validator as TurnPlanValidator
    participant Clarify as ClarifyResponder
    participant Task as TaskHandler
    participant Knowledge as KnowledgeHandler
    participant Chitchat as ChitchatHandler

    Engine->>Engine: _prepare_session(state)
    Engine->>State: begin_turn(user_message)
    Engine->>Planner: predict(state, flows, intents)
    Planner-->>Engine: TurnPlan
    Engine->>Validator: validate(state, turn_plan, flows, intents)
    Validator-->>Engine: TurnPlanValidationResult

    alt valid == false
        Engine->>Clarify: respond(state, reason)
        Clarify-->>Engine: list[BotMessage]
    else task route
        Engine->>Task: handle()
        Task-->>Engine: list[BotMessage] [占位]
    else knowledge route
        Engine->>Knowledge: handle()
        Knowledge-->>Engine: list[BotMessage] [占位]
    else chitchat route
        Engine->>Chitchat: handle()
        Chitchat-->>Engine: list[BotMessage] [占位]
    end

    Engine->>State: pending_turn.bot_messages.extend(messages)
    Engine->>State: commit_turn()
```

## 图 3：对象消息处理时序图

```mermaid
sequenceDiagram
    participant Engine as DialogueEngine
    participant State as DialogueState
    participant Task as TaskHandler
    participant Clarify as ClarifyResponder

    Engine->>Engine: _prepare_session(state)
    Engine->>State: begin_turn(user_message)
    Engine->>State: set_focused_object(user_message.object)
    Engine->>Engine: _resolve_object_commands(messages, state, flows)

    alt commands exists
        Engine->>Task: handle()
        Task-->>Engine: list[BotMessage] [占位]
    else active_task exists
        Engine->>Task: handle()
        Task-->>Engine: list[BotMessage] [占位]
    else no commands and no active_task
        Engine->>Clarify: respond(state, OBJECT_REQUIRES_INTENT)
        Clarify-->>Engine: list[BotMessage]
    end

    Engine->>State: commit_turn()
```

## 图 4：Plan / Validator / Clarify 类图

```mermaid
classDiagram
    class TurnPlanner {
      +predict(dialogue_state: DialogueState, flows: FlowList, intents: dict[str, KnowledgeIntent]): TurnPlan
      +_build_input_prompt(dialogue_state: DialogueState, flows_list: FlowList, intents: dict[str, KnowledgeIntent]): dict[str, Any]
      +_predict_from_inputs_prompt(prompt): TurnPlan
    }

    class TurnPlanValidator {
      +validate(state: DialogueState, turn_plan: TurnPlan, flows: FlowList, intents: dict[str, KnowledgeIntent]): TurnPlanValidationResult
      +_get_active_tracks(turn_plan: TurnPlan): list[str]
      +_validate_task(turn_plan: TurnPlan, flows: FlowList): TurnPlanValidationResult
      +_validate_knowledge(turn_plan: TurnPlan, state: DialogueState, intents: dict[str, KnowledgeIntent]): TurnPlanValidationResult
    }

    class ClarifyResponder {
      +respond(state: DialogueState, reason: ClarifyReason): list[BotMessage]
      +build_clarify_message(reason: ClarifyReason, state: DialogueState): str
    }
```

## 图 5：`TurnPlan` 三轨结构图

```mermaid
classDiagram
    class TaskTurnPlan {
      +commands: list[Command]
      +from_dict(data: dict): TaskTurnPlan
    }

    class KnowledgeTurnPlan {
      +intents: list[str]
      +from_dict(data: dict): KnowledgeTurnPlan
    }

    class ChitchatTurnPlan

    class TurnPlan {
      +task: TaskTurnPlan | None
      +knowledge: KnowledgeTurnPlan | None
      +chitchat: ChitchatTurnPlan | None
      +from_dict(data: dict): TurnPlan
    }

    class TurnPlanValidationResult {
      +valid: bool
      +reason: ClarifyReason | None
    }

    TurnPlan --> TaskTurnPlan
    TurnPlan --> KnowledgeTurnPlan
    TurnPlan --> ChitchatTurnPlan
    TurnPlanValidator ..> TurnPlanValidationResult
```

## `_build_input_prompt(...)` 七类输入材料

| 输入项 | 来源 | 作用 |
| --- | --- | --- |
| `user_message` | `pending_turn.user_message` | 当前轮用户表达 |
| `current_conversation` | `current_session().turns[-10:]` | 最近对话历史 |
| `active_task_json` | `state.active_task` | 当前活跃任务 |
| `interrupted_tasks_json` | `state.paused_tasks` | 被打断任务列表 |
| `focused_object_json` | `state.focused_object` | 当前焦点对象 |
| `available_flows_json` | `FlowList.flows` 去掉 `steps` 后序列化 | 当前可选业务流程 |
| `knowledge_intents_json` | `KnowledgeIntent` 列表 | 当前知识类意图词典 |

## 当前状态结论

| 组件 | 当前状态 | 说明 |
| --- | --- | --- |
| `DialogueEngine` 主骨架 | `[已实现]` | 已能处理文本 / 对象分支 |
| `TurnPlanner` | `[已实现]` | 已能打包物业版输入材料并调 LLM |
| `TurnPlanValidator` | `[已实现]` | 已有 task / knowledge / chitchat 最小校验 |
| `ClarifyResponder` | `[已实现]` | 已切成物业语义澄清 |
| `TaskHandler.handle()` | `[占位]` | 入口在，但执行逻辑未落地 |
| `KnowledgeHandler.handle()` | `[占位]` | 入口在，但执行逻辑未落地 |
| `ChitchatHandler.handle()` | `[占位]` | 入口在，但执行逻辑未落地 |

## 一句话结论

当前最完整的一段是“理解 -> 规划 -> 校验 -> 澄清 / 分轨”这条决策链，真正的执行层还停在三个 handler 入口上。
