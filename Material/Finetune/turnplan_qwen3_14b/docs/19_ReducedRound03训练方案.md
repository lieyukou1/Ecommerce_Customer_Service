# Reduced round_03 训练方案

- 最后修改时间: `2026-06-07`
- 文档定位: `round_03` 前置重定义完成后的收缩版 SFT 训练方案
- 上级入口: [17_Round03前置重定义方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/17_Round03前置重定义方案.md)

## 1. 方案目标

reduced `round_03` 不再试图全面优化统一 TurnPlan。

本轮只验证一件事:

**在高损失 `read-only` 已由 runtime 吸收后, 小规模 SFT 能否稳定提升剩余三类核心能力。**

这三类核心能力固定为:

1. `ambiguous_all_null`
2. `active_task_slot_fill`
3. `task_interrupt_resume_cancel`

如果这三类都不能稳定优于未训练基座, 就视为 reduced `round_03` 不成立。

## 2. 主任务边界

### 保留的主任务

- 模糊表达时, 是否应进入 `all_null / clarify fallback`
- 当前已有 `active_task / active_system_task` 时, 是否能把短句识别为补槽
- `cancel_flow` 和 `directive.exit_runtime` 的边界判断
- 办理类主轨的基本稳定性

### 明确不再作为主学习负担的部分

以下场景已经通过 runtime 吸收明显降低训练压力, 不再作为 unified SFT 主矛盾:

- `resident_work_orders_list_query`
- `resident_service_items_list_query`
- `work_order_status_query`
- `service_progress_tracking`
- 大部分 `service_item_detail_query`

这部分仍保留 system-level eval, 但不再主导 reduced `round_03` 的训练结论。

## 3. 主训练桶设计

### 主攻桶

| bucket | 角色 | 说明 |
| --- | --- | --- |
| `ambiguous_all_null` | 主攻 1 | 解决“别过早强行进入 task” |
| `active_task_slot_fill` | 主攻 2 | 解决 active context 下的短句补槽 |
| `task_interrupt_resume_cancel` | 主攻 3 | 解决取消 / 恢复 / 切换 / 退出边界 |

### 稳定锚点桶

| bucket | 角色 | 说明 |
| --- | --- | --- |
| `directive_exit_runtime` | 锚点 | 防止 `exit_runtime` 能力回退或漂移 |
| `work_order_business_urge` | 锚点 | 防止 task 主轨过度收缩 |
| `work_order_business_complaint` | 锚点 | 防止 task 主轨过度收缩 |

### 默认不进入主训练集的桶

- `work_order_read_only_task`
- `service_item_knowledge`
- `object_context_followup`
- `chitchat`

这些桶不是不重要, 而是本轮先不让它们干扰主矛盾。

若后续需要保留少量作对照, 也只允许以“锚点审计样本”身份进入, 不允许主导训练结论。

## 4. 数据规模策略

### 目标规模

reduced `round_03` 的目标数据规模建议为:

| bucket | train target | val target |
| --- | ---: | ---: |
| `ambiguous_all_null` | 80 | 20 |
| `active_task_slot_fill` | 80 | 20 |
| `task_interrupt_resume_cancel` | 80 | 20 |
| `directive_exit_runtime` | 40 | 10 |
| `work_order_business_urge` | 30 | 8 |
| `work_order_business_complaint` | 30 | 8 |

目标总量:

- train: `340`
- val: `86`

### 当前现实约束

现有 phase1 canonical 数据还不足以直接满足上面的目标配额。

因此 reduced `round_03` 分两步:

1. 先从现有 canonical 数据切出 `base slice`
2. 再按主攻桶补充或重写样本到目标规模

## 5. 每个主攻桶的增强方向

### `ambiguous_all_null`

目标:

- 教模型在信息不充分时先停住
- 不因为一句话“像需求”就直接进 flow

优先覆盖:

- 对象不清
- flow 不唯一
- 只有槽位碎片, 但不足以推进
- 带动作倾向词, 但无法唯一落轨

### `active_task_slot_fill`

目标:

- 教模型在 active context 下识别“短句也可能是补槽”

优先覆盖:

- 原因短句
- 确认短句
- 时间短句
- 电话短句
- 纯名词 / 纯短语补充

硬约束:

- 每条样本必须真实带 `active_task` 或 `active_system_task`
- 不允许用空 runtime 去伪造补槽样本

### `task_interrupt_resume_cancel`

目标:

- 教模型稳定区分:
  - 恢复刚才任务
  - 取消当前 flow
  - 退出当前上下文
  - 从当前任务切换到另一个任务

优先覆盖:

- `cancel_flow vs exit_runtime` 成对对照
- `resume_flow` 与“重新发起同任务”的对照
- 任务切换时的 flow 变更

## 6. 泛化风险与抑制策略

reduced `round_03` 的主要风险不是“训不动”, 而是“训窄了”。

### 风险 1: 主桶提分, 邻近语义泛化变差

缓解:

- 保留 `urge / complaint / directive` 三个锚点桶
- 不只看主桶分数, 必须跑 smoke 与 scenario replay

### 风险 2: 模型变得过度保守或过度 eager

缓解:

- `ambiguous_all_null` 不单独决定成败
- 同时观察 `task_command_family_accuracy`
- 同时观察 `slot_fill_exact_match`

### 风险 3: 把已解决的 `read-only` 问题重新放回模型肩上

缓解:

- runtime 吸收逻辑继续保留
- `high_loss_read_only_metrics` 继续单列评测
- reduced `round_03` 禁止回到“让统一 SFT 硬背 read-only 协议边界”的路线

## 7. 训练与评测口径

### 主指标

reduced `round_03` 主看:

1. `ambiguous_all_null` bucket accuracy
2. `active_task_slot_fill` bucket accuracy
3. `task_interrupt_resume_cancel` bucket accuracy
4. `task_command_family_accuracy`
5. `slot_fill_exact_match`

### 守门指标

继续单列:

- `high_loss_read_only_metrics.system_success_rate`
- `knowledge_false_positive_rate`
- 表达层 smoke 结果

## 8. 晋级门槛

候选只有在下面条件同时满足时才允许晋级:

1. `ambiguous_all_null` 明显优于 base
2. `active_task_slot_fill` 明显优于 base
3. `task_interrupt_resume_cancel` 明显优于 base
4. `high_loss_read_only_metrics.system_success_rate` 不明显回退
5. smoke 与 scenario replay 不出现新的结构性副作用

如果只提升 1 个主桶, 视为不晋级。

## 9. 实施顺序

1. 完成 reduced 数据切分规范
2. 从现有 canonical 数据切出 `base slice`
3. 审核 `base slice` 是否符合主任务边界
4. 判断需补强的样本规模
5. 完成 targeted augmentation
6. 在 reduced 口径下重跑 base baseline
7. 若增益空间明确, 再开启 reduced `round_03` SFT

## 10. 当前阶段结论

当前已经可以确定的是:

- 这轮不该再做“完整 TurnPlan 再试一轮”
- 这轮应该做“收缩版、更可证伪的专项实验”
- 现阶段最值得花预算的, 是主攻三类残余主错法, 而不是继续纠缠高损失 `read-only` 边界
