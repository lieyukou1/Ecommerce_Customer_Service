# Reduced round_03 数据切分与扩样规范

- 最后修改时间: `2026-06-07`
- 文档定位: reduced `round_03` 的数据切分、保留、扩样与验收规范
- 上级入口: [19_ReducedRound03训练方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/19_ReducedRound03训练方案.md)

## 1. 文档目标

本规范回答 4 件事:

1. 先从现有 phase1 canonical 数据里保留哪些桶
2. 这些桶怎么切成 reduced `base slice`
3. 哪些桶需要后续扩样
4. 扩样时有哪些硬约束不能破

## 2. reduced `base slice` 的保留桶

现阶段 reduced `base slice` 固定保留 6 个桶:

- `ambiguous_all_null`
- `active_task_slot_fill`
- `task_interrupt_resume_cancel`
- `directive_exit_runtime`
- `work_order_business_urge`
- `work_order_business_complaint`

## 3. 当前可直接切出的基础规模

基于现有 canonical 数据, 可直接切出的 reduced `base slice` 规模为:

| bucket | train | val |
| --- | ---: | ---: |
| `ambiguous_all_null` | 35 | 6 |
| `active_task_slot_fill` | 50 | 10 |
| `task_interrupt_resume_cancel` | 45 | 7 |
| `directive_exit_runtime` | 35 | 6 |
| `work_order_business_urge` | 30 | 5 |
| `work_order_business_complaint` | 30 | 5 |

总量:

- train: `225`
- val: `39`

这是一版**可直接使用的底板**, 不是最终目标配额。

## 4. reduced `base slice` 的切分原则

### 原则 1: 先保留整桶, 不先做细粒度裁剪

第一版 reduced `base slice` 直接按桶整批保留, 不在当前阶段先做:

- 句式手工筛掉一半
- 人工挑“最优样本”
- 用主观印象删个别样本

原因:

- 先保证可复现
- 先让 reduced 口径有稳定底板
- 细粒度样本修剪应放在下一步 targeted augmentation 之后再做

### 原则 2: runtime 相关桶先整桶剥离

以下桶默认不进入 reduced `base slice`:

- `work_order_read_only_task`
- `service_item_knowledge`
- `object_context_followup`
- `chitchat`

其中:

- `work_order_read_only_task` 是 runtime 已吸收的主矛盾转移源
- 其余桶是当前主实验的干扰项

### 原则 3: `active_task_slot_fill` 必须通过 runtime 真实性检查

该桶样本必须满足至少一项:

- `active_task` 非空
- `active_system_task` 非空

若两者同时为空, 该样本不得进入 reduced `base slice`。

### 原则 4: `ambiguous_all_null` 只保留真正的四字段全空

该桶 gold output 必须满足:

- `task = null`
- `knowledge = null`
- `chitchat = null`
- `directive = null`

任何“表面模糊但实际上已给出 flow”的样本, 不得混入此桶。

## 5. 后续扩样优先级

reduced `round_03` 的扩样优先级固定如下:

### P0

- `ambiguous_all_null`
- `active_task_slot_fill`
- `task_interrupt_resume_cancel`

### P1

- `directive_exit_runtime`

### P2

- `work_order_business_urge`
- `work_order_business_complaint`

解释:

- P0 是主错法核心
- P1 是为了守住边界
- P2 是为了防止 task 主轨过度收缩

## 6. 扩样写作规则

### `ambiguous_all_null`

必须遵守:

- 用户看起来像在办事
- 但仍不足以唯一决定 flow
- 不允许自我标注“我是在问这个 / 我是在补这个”

### `active_task_slot_fill`

必须遵守:

- 用户直接说内容, 不解释自己在补槽
- 短句优先
- 样本必须依赖当前 runtime 才能判断

### `task_interrupt_resume_cancel`

必须遵守:

- 成对写
- 同类话术在不同 runtime 下允许落不同标签
- 明确区分:
  - 取消 flow
  - 退出 runtime
  - 恢复 flow
  - 切换任务

## 7. 数据切分后的验收门槛

reduced `base slice` 切出后必须满足:

1. 桶集合与本规范一致
2. `active_task_slot_fill` 不存在 runtime 为空的脏样本
3. `ambiguous_all_null` 全部四字段为 `null`
4. `directive_exit_runtime` 全部为 `directive.action = exit_runtime`
5. train / val 文件与 manifest 可复现

## 8. 当前阶段产物要求

切分完成后至少产出:

- `records_train.jsonl`
- `records_val.jsonl`
- `manifest.json`
- `summary.md`

这些文件用于回答:

- reduced `base slice` 保留了哪些桶
- 各桶数量是多少
- 哪些桶被整桶剥离
- 哪些验收检查已通过

## 9. 当前阶段不做的事

- 不直接把扩样后的目标配额一次性写满
- 不先把所有保留样本再重写一遍
- 不一边切分一边改标签
- 不在没有 manifest 的前提下手工随意删样本

## 10. 当前结论

现阶段最合理的动作不是“再讨论要不要 reduced”, 而是:

1. 先把 reduced `base slice` 切出来
2. 用这版底板作为后续扩样和专项训练的真相源
3. 所有后续补强都围绕这版底板追加, 不再回到 full unified 口径
