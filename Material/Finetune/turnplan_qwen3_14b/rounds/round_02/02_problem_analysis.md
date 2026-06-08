# round_02 Problem Analysis

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/00_run_manifest.md)
- 原始指标: [qwen3_14b_turnplan_round2_20260607b_val_metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_val_metrics.json)
- 失败摘要: [qwen3_14b_turnplan_round2_20260607b_val_failure_summary.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_val_failure_summary.json)
- 预测明细: [qwen3_14b_turnplan_round2_20260607b_val_predictions.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_val_predictions.jsonl)

## 先看结论

- 这轮没有格式问题: `json_valid_rate = 1.0`
- `all_null` 评测噪声已经被剥离干净
- `task_command_family_accuracy` 比 round 1 有回升, 但只回升到 `0.5814`
- `work_order_read_only_task` 仍然是主失败桶, 且失败数仍是 `11`
- 失败已经高度收缩为“语义决策偏移”, 不是协议格式崩坏
- 新增系统性诊断后确认: **round_02 不仅没有稳定压过未训练基座, 在 train split 上也没有压过**

## 与未训练基座的同口径诊断

- 诊断报告: [qwen3_14b_round2_systemic_diagnostic.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_round2_systemic_diagnostic.md)
- 指标摘要: [qwen3_14b_round2_systemic_diagnostic_summary.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_round2_systemic_diagnostic_summary.json)

核心结论:

- `val` 上:
  - `top_level_track_accuracy` 持平
  - `task_command_family_accuracy` 低于基座
  - `protocol_gate_pass_rate` 明显低于基座
  - `knowledge_false_positive_rate` 高于基座
- `train` 上:
  - `top_level_track_accuracy` 低于基座
  - `task_command_family_accuracy` 低于基座
  - `flow_selection_accuracy` 低于基座
  - `protocol_gate_pass_rate` 低于基座

这意味着:

- 问题已经不能再解释成“只是验证集泛化差”
- 至少对当前任务切法来说, 微调候选连训练分布本身都没有学出比基座更强的协议行为

## 错误分布

### 按 bucket

| bucket | effective_failure_count | 主错法 |
| --- | ---: | --- |
| work_order_read_only_task | 11 | `task -> knowledge` 为主, 夹杂少量 `task -> all_null` |
| task_interrupt_resume_cancel | 3 | `cancel_flow -> directive.exit_runtime`, `task -> all_null` |
| active_task_slot_fill | 2 | `task -> knowledge`, `task -> all_null` |
| chitchat | 1 | `chitchat -> knowledge` |
| work_order_business_complaint | 1 | `task -> all_null` |

### 按错法机制

- `track_mismatch`: `18`
- `json_invalid`: `0`
- `pure_gate_only_failure`: `0`

这说明本轮的主要问题已经不是“输出不合法”, 而是“输出合法, 但轨道判断仍偏”。

## 相比 round_01 的变化

### 1. 评测口径问题已经收干净

- round 1 里的 `ambiguous_all_null` 5 条不再污染失败统计
- `adjusted_protocol_gate_pass_rate = 0.9125` 说明真实的可用通过率比原始 gate 指标更接近实际情况

### 2. 保守收缩略有改善, 但 improvement 还不够

- `task_command_family_accuracy`: `0.5349 -> 0.5814`
- `protocol_gate_pass_rate`: `0.8375 -> 0.8500`

这说明:
- 调低学习率不是白做
- 小范围样本修订也不是完全无效
- 但它们没有触及主矛盾

### 3. 主矛盾没有动

`work_order_read_only_task` 仍然 11 条失败, 具体表现为:
- 查状态/进度/费用/详情/列表, 仍被打成 `knowledge`
- 少量样本仍被打回 `all_null`

这说明我们上一轮“只改 4 条 read-only 对照样本”的力度过小, 不足以改变模型的主偏好。

## 根因拆解

### 1. `work_order_read_only_task` 还是强烈偏向 `knowledge`

代表失败:
- `tp_work_order_read_only_task_val_000`
- `tp_work_order_read_only_task_val_001`
- `tp_work_order_read_only_task_val_002`
- `tp_work_order_read_only_task_val_004`
- `tp_work_order_read_only_task_val_005`
- `tp_work_order_read_only_task_val_008`
- `tp_work_order_read_only_task_val_010`
- `tp_work_order_read_only_task_val_011`
- `tp_work_order_read_only_task_val_014`

判断:
- 这不是 flow 细分错误
- 也不是 JSON 合同错误
- 本质仍是 `task vs knowledge` 协议边界没有被教稳

更具体地说:
- 用户语言越像“咨询解释”, 模型越容易退回知识轨道
- 但项目协议要求这类只读查询仍然走 `task`
- 基座与候选的对照进一步说明:
  - 这不是候选“偶然发挥差”
  - 而是微调后模型在这条反常识边界上被拉偏了

### 2. `active_task_slot_fill` 仍存在“短句补槽被看丢”

代表失败:
- `tp_active_task_slot_fill_val_000`: `task -> knowledge`
- `tp_active_task_slot_fill_val_006`: `task -> all_null`

判断:
- 这类错法比 round 1 少了, 但没有清零
- 说明 active context 的利用仍然不够强
- 单靠降学习率不能解决

### 3. `cancel_flow vs exit_runtime` 仍未学稳

代表失败:
- `tp_task_interrupt_resume_cancel_val_001`
- `tp_task_interrupt_resume_cancel_val_005`

共同模式:
- 用户仍在当前业务流里说“先不弄了”
- gold 是 `cancel_flow`
- 模型预测成 `directive.exit_runtime`

说明:
- round 2 的小补样本只让这条边界“可见了”
- 但还没有形成稳定的语义分界

### 4. 表达层 smoke 没出结构性污染

这是好消息:
- 没有 JSON 混入
- 没有明显发硬
- 没有过短回复
- 没有拒答

说明统一模型替换到 `knowledge / clarify / chitchat` 这一步, 至少在 smoke 集上没有暴露新的硬伤。

## 诊断后新增判断

### 1. 这更像“任务定义 / 标签边界 / SFT 塑形方式”问题

支持证据:

- 基座在 `train` 与 `val` 两侧都压过候选
- 最大失败桶两轮不动
- 失败模式高度稳定, 仍集中在 `task vs knowledge`

### 2. 暂时不应继续按“补几条样本 -> 再开一轮”处理

支持证据:

- round 2 的小补强只带来轻微纠偏
- 但没有触及主失败机制
- 如果继续同路线堆轮次, 很可能只是消耗更多时间而不换来结构性改善

## 暂时不支持的解释

### 1. “round 2 还是主要被评测口径拖累”

不成立。
因为 5 条 clarify fallback 已经单列剥离, 真实失败仍有 18 条。

### 2. “flow 细分才是主问题”

不成立。
`flow_selection_accuracy` 没有改善, 但更上游的 `track_mismatch` 依旧占绝对主导。

### 3. “这轮需要再靠继续降学习率来救”

目前证据不足。
学习率已经从 `1e-4` 降到 `5e-5`, 指标有轻微回升, 但 read-only 主问题基本没动。
下一轮如果继续只动学习率, 很大概率只是细调, 不是破局。
