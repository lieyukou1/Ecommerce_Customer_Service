# round_03 Next Round Plan

## 当前状态

重定义后的 baseline replay 已完成。  
reduced SFT 也已经真实跑过一轮。

当前结论不是“继续盲训”，而是:

1. schema 不用改
2. 高损失 `read-only` 继续交给 runtime
3. 先修 reduced 数据集里的目标桶拉扯，再考虑下一轮训练

## 下一步固定顺序

1. 固定 `no-thinking serving` 为 TurnPlan 评测默认配置
2. 针对 `active_task_slot_fill` 做 targeted dataset repair
3. 针对 `task_interrupt_resume_cancel` 做少量对照补样
4. 暂时不扩 `ambiguous_all_null`，先控制它的训练权重
5. 在同超参下重跑一轮 reduced SFT

## 数据结构是否需要改

不需要。

继续沿用当前 canonical schema:

- `id / source / bucket / split / input / output / meta`
- `input.history / runtime_state / active_task / active_system_task / paused_tasks / focused_object / user_message`
- `output.task / knowledge / chitchat / directive`

下一轮改的是:

- 样本配比
- 对比样本设计
- targeted augmentation 的覆盖点

不是:

- schema 改造
- protocol 改造
- label 字段重命名

## 下一轮数据修复重点

### 1. `active_task_slot_fill`

目标:

- 把当前被 `all_null / knowledge` 吸走的 active-context 短句补槽修回来

新增样本要求:

- 必带 `active_task`
- 尽量带 `active_system_task=system_collect_information`
- 用户话术保持短、自然、不自我标注
- gold 尽量是 **纯 `set_slots`**
- 覆盖:
  - `service_item_id`
  - `rule_topic`
  - `urge_reason`
  - `complaint_reason`
  - `contact_phone`
  - `complaint_confirm`

### 2. `task_interrupt_resume_cancel`

目标:

- 稳住“从催办切投诉”
- 稳住“取消当前 flow”与“退出当前上下文”的边界

新增样本要求:

- 必带 active flow 或 paused context
- 同一语义做成最小对照:
  - 取消 flow
  - 退出当前对象 / 话题
  - 从当前 flow 切到投诉

### 3. `ambiguous_all_null`

处理原则:

- 这一桶已经学到东西了
- 下一轮先**不扩量**
- 如需进入训练，考虑限制采样权重，避免继续把模型推向过度保守

## 下一轮训练默认不改的东西

先不改:

- base model: `Qwen/Qwen3-14B`
- 训练方式: `QLoRA`
- epoch: `2`
- 学习率: `3e-5`

原因:

- 当前证据更像数据配比 / 对比信号问题
- 先保持超参不动，便于隔离变量

## 下一轮主指标

主看:

- `active_task_slot_fill` bucket accuracy
- `task_interrupt_resume_cancel` bucket accuracy
- `task_command_family_accuracy`
- `slot_fill_exact_match`
- `adjusted_protocol_gate_pass_rate`

继续观察:

- `ambiguous_all_null` bucket accuracy
- `top_level_track_accuracy`
- `high_loss_read_only_metrics.system_success_rate`

## 当前不做的事

- 不改 schema
- 不回到“扩 read-only 对照样本为主”的路线
- 不先动 prompt 规则
- 不直接在现有 candidate 上补训续跑

## 紧接着要做的事

1. 参考 [reduced_round03_targeted_repair_list.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/artifacts/reduced_round03_targeted_repair_list.md)
2. 切出 `active_task_slot_fill + interrupt/cancel` 的 focused repair 清单
3. 产出下一版 reduced 数据集
