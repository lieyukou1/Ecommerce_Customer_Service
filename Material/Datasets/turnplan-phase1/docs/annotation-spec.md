# TurnPlan 标注规范

- 最后修改时间：2026-06-06 17:00
- 文档定位：Phase 1 样本标注硬规则
- 上级入口：[turnplan-phase1/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/README.md)
- 下级入口：[offline-evaluation.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/docs/offline-evaluation.md)

## 1. 任务边界

- 本期只标 `TurnPlan`，不标最终客服回复文本。
- 顶层只允许：
  - `task`
  - `knowledge`
  - `chitchat`
  - `directive`
- 一次只允许一个主轨道非空。
- 如果方向不明确，四个字段全 `null`。

## 2. 输入字段白名单

标注时只允许使用以下上下文：

- `history`：最近 1-3 轮用户/机器人文本
- `runtime_state`
  - `conversation_state`
  - `last_route`
  - `last_task_outcome`
- `active_task`
- `active_system_task`
- `paused_tasks`
- `focused_object`
- `user_message`

明确不放入第一阶段输入：

- 完整 `sessions`
- `pending_turn`
- 原始数据库整段 JSON
- 与当前决策无关的归档历史

## 3. 轨道标注规则

### 3.1 directive

- 当语义是“结束当前上下文 / 这段话题 / 这个对象”时，一律标：
  - `{"directive": {"action": "exit_runtime"}}`
- 典型表达：
  - “先这样”
  - “退出当前这个”
  - “不看这个了”
  - “重新开始”
  - “先聊别的”

### 3.2 task

- 用户明确进入办理流程，或继续当前业务流程，标 `task`
- 当前只允许命令：
  - `start_flow`
  - `resume_flow`
  - `cancel_flow`
  - `set_slots`

工单相关固定口径：

- 围绕工单状态、进度、处理到哪、费用怎么算等只读追问：
  - 允许落到 `task` 的只读 flow
  - 不标 `knowledge`
- 围绕工单催办：
  - `start_flow = work_order_urge_submission`
- 围绕工单投诉：
  - `start_flow = complaint_request_submission`
- 当前有 `active_task` 或 `active_system_task=system_collect_information`：
  - 优先判断是不是继续当前任务、补当前槽位

### 3.3 knowledge

- 用户是在“了解信息”，而不是“推进办理”，标 `knowledge`
- 服务项目默认优先走 `service_item_info`
- 如果服务项目当前没有明确可执行 flow，即使用户说“我想直接办一下”，也不要虚构 task

### 3.4 chitchat

- 纯寒暄、闲聊、情绪表达、自我介绍
- 例如：
  - “你好”
  - “你是谁”
  - “今天辛苦了”

### 3.5 all null

- 看起来像要办事，但方向不足以唯一落到某个轨道
- 例如：
  - “这个你帮我处理一下”
  - “那你看着办吧”
  - “我想弄一下这个事”

不要把模糊业务表达错标成 `chitchat`。

## 4. directive 与 cancel_flow 的区分

- `directive.exit_runtime`
  - 结束当前上下文、对象或整段对话链
- `cancel_flow`
  - 用户仍在围绕当前业务 flow 办事，只是取消这个 flow

优先级固定：

- “结束当前上下文”优先于 `cancel_flow`
- 不允许实现者临场改口径

## 5. 服务项目知识口径

- Phase 1 默认服务项目信息咨询意图统一用：
  - `service_item_info`
- 典型问题：
  - 收费
  - 办理方式
  - 服务说明
  - 是否可预约
  - 去哪里领 / 去哪里办

## 6. 工单只读口径

围绕已聚焦工单的只读追问，优先落以下 flow：

- `work_order_status_query`
- `service_progress_tracking`

是否同时标 `set_slots`：

- 如果上下文已明确给出 `work_order_id`，允许同轮补：
  - `{"command": "set_slots", "slots": {"work_order_id": "..."}}`

## 7. 当前任务补槽口径

如果存在：

- `active_task`
- 或 `active_system_task.flow_id = "system_collect_information"`

且用户当前回答本质上是在补：

- 原因
- 说明
- 联系方式
- 确认信息
- 时间信息

则优先标：

- `task.commands = [{"command": "set_slots", ...}]`

## 8. source 字段口径

- `repo-scenario`
  - 直接源自仓库现有长对话场景模式
- `hand-crafted`
  - 人工扩写、受控改写、但仍遵守当前协议
- `history-backed`
  - 预留给 Phase 2 历史对话接入，本期不作为主依赖

## 9. 审核规则

- 黄金样本全量人工复核
- 扩写样本至少抽检 25%
- 发现规则冲突时，先修文档口径，再修样本
- 不允许按个人直觉直接改标签
