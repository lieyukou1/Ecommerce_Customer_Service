# round_01 to round_02 Plan

- 上一轮结论：[03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/03_decision_log.md)

## 下一轮要改什么

### 1. 先改评测口径

- 从主失败统计里剥离：
  - `all_null_as_expected_clarify_fallback`
- 保留记录，但不再当成模型退化主证据

### 2. 调整训练超参

- learning rate：`1e-4 -> 5e-5`
- 先不改：
  - epoch
  - LoRA rank / alpha / dropout
  - `qwen3_nothink` 口径

### 3. 做最小必要数据调整

第一优先级：

- `work_order_read_only_task`
- 补 task / knowledge 成对对照样本
- 目标是教边界，不是单纯加量

第二优先级：

- `active_task_slot_fill`
- 先核查：
  - `active_task` 是否真的非空
  - `active_system_task` 是否真的指向当前 target slot
- 核查通过后再决定补量

第三优先级：

- `cancel_flow vs directive.exit_runtime`
- 只做小批量对照增强

## 下一轮不改什么

- 不优先做 flow 级 hard case 强化
- 不在 prompt 中新增大段“哪些句子不属于 knowledge”的负向枚举
- 不在 round_01 candidate checkpoint 上继续补训
- 不把 `top_level_track_accuracy` 当主晋级门槛

## 下一轮评测重点

主看：

1. `task_command_family_accuracy`
2. `work_order_read_only_task` bucket accuracy
3. `knowledge_false_positive_rate`

参考看：

- `top_level_track_accuracy`
- `flow_selection_accuracy`
- `protocol_gate_pass_rate`

## 晋级门槛

- 候选必须优于本地未训 `Qwen3-14B`
- `task_command_family_accuracy` 至少回到 `0.60+`
- `knowledge_false_positive_rate` 需要明显下降
- `work_order_read_only_task` bucket 不允许继续成为主失败桶
- 表达层 smoke 不得出现稳定 JSON 污染或明显语气发硬

## 推荐执行顺序

1. 改评测口径
2. 核查 `active_task_slot_fill` 状态字段
3. 补 `work_order_read_only_task` 对照样本
4. 小补 `cancel_flow vs exit_runtime`
5. 以 `lr=5e-5` 重开新 run
6. 重新做 runtime replay 与 smoke
