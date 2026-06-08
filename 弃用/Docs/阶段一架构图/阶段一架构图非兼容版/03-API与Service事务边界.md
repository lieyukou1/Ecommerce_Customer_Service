# 03-API与Service事务边界

## 这册看什么

这一册回答：

1. `/api/chat` 是怎么翻译输入输出的
2. `DialogueService` 怎么定义事务边界
3. API 与 Service 的类关系是什么

它不讲 planner 和 task 轨内部细节。

## 图 1：请求与响应模型转换图

```mermaid
flowchart LR
    ChatRequest["ChatRequest"] --> BuildUser["_build_user_message(...)"]
    BuildUser --> UserMessage["UserMessage"]
    UserMessage --> Service["DialogueService.process_message(...)"]
    Service --> ProcessResult["ProcessResult"]
    ProcessResult --> BuildResp["_build_chat_response(...)"]
    BuildResp --> ChatResponse["ChatResponse"]
```

## 图 2：`DialogueService` 事务边界图

```mermaid
sequenceDiagram
    participant Router as chat_router.chat
    participant Service as DialogueService
    participant Repo as DialogueStateRepository
    participant Engine as DialogueEngine

    Router->>Router: _build_user_message(chat_request)
    Router->>Service: process_message(user_message)
    Service->>Repo: load(user_message.resident_id)
    Repo-->>Service: DialogueState
    Service->>Engine: hand_dialogue(dialogue_state, user_message)
    Engine-->>Service: ProcessResult
    Service->>Repo: save(dialogue_state)
    Repo-->>Service: commit done
    Service-->>Router: ProcessResult
    Router->>Router: _build_chat_response(process_result)
```

## 图 3：API / Service 类图

```mermaid
classDiagram
    class ChatObject {
      +type: str
      +id: str
      +title: str | None
      +attributes: dict
    }

    class ChatRequest {
      +resident_id: str
      +message_id: str | None
      +text: str | None
      +object: ChatObject | None
    }

    class ChatBotMessage {
      +text: str | None
      +object: ChatObject | None
    }

    class ChatResponse {
      +resident_id: str
      +message_id: str
      +messages: list[ChatBotMessage]
    }

    class DialogueService {
      -dialogue_state_repository: DialogueStateRepository
      -dialogue_engine: DialogueEngine
      +process_message(user_message: UserMessage): ProcessResult
    }

    ChatRequest --> ChatObject
    ChatResponse --> ChatBotMessage
    DialogueService --> DialogueStateRepository
    DialogueService --> DialogueEngine
```

## 边界说明表

| 问题 | 放在哪层 | 原因 |
| --- | --- | --- |
| `resident_id`、`text`、`object` 的 HTTP 协议校验 | API | 这是接口契约 |
| `ChatRequest -> UserMessage` 的翻译 | API | 这是接口壳到领域对象的装配 |
| `load -> engine -> save` 的编排 | Service | 这是一次完整事务的边界 |
| 对话状态如何变化 | Engine / Domain | 这是核心业务逻辑 |

## 一句话结论

API 负责翻译，Service 负责事务编排，真正的对话决策不在这两层里展开。
