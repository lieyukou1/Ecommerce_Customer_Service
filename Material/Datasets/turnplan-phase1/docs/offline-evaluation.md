# TurnPlan 离线评测口径

- 最后修改时间：2026-06-06 17:00
- 文档定位：Phase 1 数据与模型离线验收口径
- 上级入口：[turnplan-phase1/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/README.md)
- 下级入口：[history-backed-phase2-spec.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/docs/history-backed-phase2-spec.md)

## 1. 静态数据验收

必须全部满足：

- 100% 样本能通过 canonical schema 校验
- 100% `output` 只包含允许字段
- 100% 样本满足“单轨或全 null”
- 100% `task.commands` 在白名单内
- 100% `directive.action` 仅为 `exit_runtime`

## 2. 数据分布验收

- `450 train + 80 val`
- 10 个 bucket 数量全部达标
- 每个 bucket 至少 30% 样本来自长对话上下文
- 全集至少 50% 样本带 `focused_object`
- 全集至少 25% 样本带 `active_task` 或 `active_system_task`
- 验证集至少 60% 样本来自长对话上下文

## 3. 模型评测指标

模型离线评测固定关注以下指标：

- `top_level_track_accuracy`
- `directive_accuracy`
- `all_null_accuracy`
- `knowledge_intent_accuracy`
- `task_command_family_accuracy`
- `flow_selection_accuracy`
- `slot_fill_exact_match`
- `json_valid_rate`
- `protocol_gate_pass_rate`

## 4. 下游回放评测

验证集不仅看预测文本，还要做离线回放：

1. 预测 `TurnPlan`
2. 送入 `protocol gate`
3. 按当前项目的 `state decision` 口径做人审对照

重点观察：

- 是否把 `exit_runtime` 错判成 `cancel_flow`
- 是否把服务项目办理咨询错判成虚构 task
- 是否把 active task 补槽错判成 `knowledge / chitchat`
- 是否把对象相关只读追问错打回全 `null`

## 5. Phase 1 成功标准

Phase 1 的成功，不是“模型已经上线”，而是：

- 数据结构稳定
- 标注规则稳定
- 导出格式稳定
- 离线验收口径稳定
- 可以直接接 8B-14B 中文指令模型做 SFT
