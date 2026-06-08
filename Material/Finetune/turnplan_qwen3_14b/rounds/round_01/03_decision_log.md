# round_01 Decision Log

- 轮次入口：[00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/00_run_manifest.md)
- 问题分析：[02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/02_problem_analysis.md)

## 本轮采纳的解释

### 1. `all_null -> gate reject` 不再按模型失败处理

采纳理由：

- gold 与预测完全一致
- 错误来自评测口径把 clarify fallback 混进了失败统计

最终处理：

- 第二轮开始前把它单列成 `all_null_as_expected_clarify_fallback`

### 2. `task -> knowledge` 主要靠数据对照修

采纳理由：

- 这类偏移发生在轨道层，不是 flow 层
- 相似表述在不同上下文下应有不同 label，最适合用成对样本教边界

最终处理：

- 优先补 `work_order_read_only_task` 的 task/knowledge 对照样本

### 3. `task -> all_null` 不能只归因于模型保守

采纳理由：

- 一部分样本已经存在 `active_task` 与 `active_system_task`
- 如果状态字段本身就没写对，单纯调学习率不会治本

最终处理：

- 第二轮前先核查 `active_task_slot_fill` 样本的状态字段真实性

### 4. `cancel_flow -> directive.exit_runtime` 是协议边界问题

采纳理由：

- 错误条数不多，但边界稳定复现
- 这不是大规模扩容数据能自然解决的类型

最终处理：

- 小批量补成对对照样本
- 保持现有协议边界说明，不额外加长 prompt

## 本轮明确否决的解释

### 1. 否决“先主攻 flow 细分增强”

否决理由：

- 第一轮主错因不是“已经输出 task 但 flow 选错”
- 更上游的问题是：
  - `task -> knowledge`
  - `task -> all_null`

### 2. 否决“用 prompt 负向列举硬写 task 不属于 knowledge”

否决理由：

- 14B 在 instruction following 上容易把这类负向规则过度泛化
- 容易把真正该进 knowledge 的句子也强拉进 task

### 3. 否决“继续在当前坏 checkpoint 上补训”

否决理由：

- 会失去对照可解释性
- 无法区分问题到底来自数据、口径还是超参

## 最终锁定的 round 2 调整项

1. 先剥离 `all_null_as_expected_clarify_fallback`
2. 学习率从 `1e-4` 下调到 `5e-5`
3. 优先补 `work_order_read_only_task` 的 task/knowledge 对照样本
4. 先核查 `active_task_slot_fill` 的状态字段，再决定是否补量
5. 小补 `cancel_flow vs exit_runtime` 对照样本
6. 第二轮主指标改看：
   - `task_command_family_accuracy`
   - `work_order_read_only_task` bucket accuracy
   - `knowledge_false_positive_rate`

## 本轮晋级结论

- round_01 candidate **不晋级**
- 蓝版本继续保留远程现网模型
- 新一轮实验必须从冻结基座重新启动
