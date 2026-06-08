# round_01 Problem Analysis

- 轮次入口：[00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/00_run_manifest.md)
- 原始失败摘要：[qwen3_14b_turnplan_pilot_20260607a_runtime_failure_summary.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_pilot_20260607a_runtime_failure_summary.json)
- 失败样本明细：[qwen3_14b_turnplan_pilot_20260607a_runtime_failures.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_pilot_20260607a_runtime_failures.jsonl)

## 错误分布

### 按 bucket

| bucket | failure_count | 主错法 |
| --- | ---: | --- |
| work_order_read_only_task | 11 | `task -> knowledge` 为主，夹杂少量 `task -> all_null` |
| ambiguous_all_null | 5 | gold 与预测都是 `all_null`，但 protocol gate 拒绝 |
| active_task_slot_fill | 3 | `task -> all_null` 与 `task -> knowledge` |
| task_interrupt_resume_cancel | 3 | `cancel_flow -> directive.exit_runtime`、`task -> all_null` |
| work_order_business_complaint | 1 | `task -> all_null` |

### 按错法机制

- `task -> knowledge`：10 条
- `task -> all_null`：6 条
- `all_null -> gate reject`：5 条
- `cancel_flow -> directive.exit_runtime`：2 条

## 真失败与伪失败拆分

### 1. `all_null -> gate reject`

这 5 条不是模型理解错了，而是：

- gold 为四字段全 `null`
- 预测也为四字段全 `null`
- 但 `TurnProtocolGate` 对无 active track 结果按 `MISSING_TRACK` 拒绝

所以它们更像：

- `all_null_as_expected_clarify_fallback`

而不是模型语义失败。

### 2. `task -> knowledge`

这是 round 1 的主错因。

问题不是 flow 选错，而是更上游的轨道偏移：

- 项目协议里属于只读 task 的查询
- 模型按自然语义把它们压成了 knowledge

高发点主要集中在：

- `work_order_status_query`
- `service_progress_tracking`
- `service_item_detail_query`
- `resident_work_orders_list_query`
- `resident_service_items_list_query`
- `resident_rule_qa`

### 3. `task -> all_null`

这类不能只用“模型偏保守”一个解释概括，需要拆成两层：

- 真保守：模型没敢起 task
- 状态未利用：当前已经有 `active_task` 或 `active_system_task`，模型还是没有把短句识别成补槽

### 4. `cancel_flow -> directive.exit_runtime`

这类是协议边界问题，不是大盘覆盖量问题。

用户语义仍在当前 flow 内，只是想取消这个 flow；  
但模型把它理解成“退出当前上下文”，于是落成了 `directive.exit_runtime`。

## 数据问题、口径问题、超参问题、协议问题

### 评测口径问题

- `all_null` 样本被 protocol gate reject 后直接混入失败统计
- 这会污染：
  - 主错因判断
  - 下一轮超参判断
  - `top_level_track_accuracy` 的解释

### 数据问题

- `task -> knowledge` 更像边界教学不足，而不是 flow 词表不够
- `active_task_slot_fill` 需要反查样本里的：
  - `active_task`
  - `active_system_task`
  - 当前 target slot
  是否与 label 真正一致

### 训练超参问题

- `task_command_family_accuracy` 从远程基线与本地基座对照看，round 1 candidate 明显偏低
- 学习率 `1e-4` 可能偏激进，放大了“保守收缩”和“上游轨道偏移”

### 协议边界问题

- `cancel_flow` 和 `directive.exit_runtime` 的边界还不够稳
- 这类问题应该通过成对对照样本和协议重申修，而不是靠大规模泛补

## 代表性失败样本

### read_only task 被打成 knowledge

- 示例入口：
  - `tp_work_order_read_only_task_val_000`
  - `tp_work_order_read_only_task_val_002`
  - `tp_work_order_read_only_task_val_014`
- 共同模式：
  - 用户说的是“查状态 / 查费用 / 看详情 / 看列表”
  - 项目协议里应起只读 task
  - 模型却按直觉打成了知识咨询

### active task 补槽被打回 all_null

- 示例入口：
  - `tp_active_task_slot_fill_val_006`
  - `tp_active_task_slot_fill_val_007`
- 共同模式：
  - 用户输入是短句
  - 当前已经有 `active_task` 与 `system_collect_information`
  - 模型没把它接成补当前槽位

### 取消 flow 被打成退出上下文

- 示例入口：
  - `tp_task_interrupt_resume_cancel_val_001`
  - `tp_task_interrupt_resume_cancel_val_005`
- 共同模式：
  - 用户在当前投诉 flow 内说“先不弄了”
  - gold 是 `cancel_flow`
  - 预测成了 `directive.exit_runtime`
