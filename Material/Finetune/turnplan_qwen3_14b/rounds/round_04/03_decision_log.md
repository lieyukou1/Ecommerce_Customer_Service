# round_04 Decision Log

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/00_run_manifest.md)
- 问题分析: [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/02_problem_analysis.md)

## 本轮采纳的决策

### 1. 保持最终 TurnPlan 输出合同不变

采纳。

原因：

- parser / gate / executor 已稳定依赖当前 `TurnPlan JSON`
- 当前更需要清理学习目标和数据输入，不是推翻运行合同

### 2. Planner 继续保持单次调用

采纳。

原因：

- 当前主问题在任务定义与数据质量，不在单次调用能力上限
- 先保持链路稳定，方便隔离变量

### 3. `read_only` runtime 兼容层先保留，并正名为正式分流层

采纳。

原因：

- 它现在承担的是高损失 read-only 的业务正确性保障
- 这比继续逼统一 SFT 硬背内部通道边界更稳

### 4. round_04 reduced 数据采用“keep + targeted_fix + bucket_rebuild”三段法

采纳。

原因：

- 全量重做成本过高
- 纯缝补又无法处理整桶时间线问题
- 三段法既保留干净底盘，也把修复焦点收紧到真正的问题桶

### 5. `active_task_slot_fill` 做 focused repair，而不是整桶丢弃

采纳。

原因：

- 它的主矛盾不是标签错，而是 lead-in 太薄、短句补槽可学性不足
- 这类问题通过补强上下文链条可以修

### 6. `ambiguous_all_null` 与 `directive_exit_runtime` 整桶重建

采纳。

原因：

- 这两桶的问题具有系统性
- 行级微修不如按决策机制重建更干净

### 7. candidate 组装阶段增加 exact duplicate 去重

采纳。

原因：

- 修复 / 重建后仍可能撞出同一对 `input + label`
- 在组装阶段统一去重，既不破坏前面三个脚本职责，也能保证训练不会白看重复对

## 本轮明确否决的决策

### 1. 否决“为了赶进度直接拿 triage 结果开训”

否决。

原因：

- triage 只是切分类，不是最终候选集
- 直接开训会把已识别的问题样本原样带进下一轮

### 2. 否决“为了凑数量放宽 `passed_for_sft` 门槛”

否决。

原因：

- 当前瓶颈不是样本条数，而是脏样本的负作用
- 先守住联合审计，再谈训练收益

### 3. 否决“现在就删掉 runtime read-only 逻辑”

否决。

原因：

- 这会把业务正确性重新暴露给尚未验证通过的边界判断
- 与当前阶段目标相反

## 本轮锁定的结论

下一步不再是继续讨论“该不该修”，而是已经形成清晰执行面：

1. 以 `reduced_round04_candidate_v1` 作为下一轮 reduced SFT 候选集
2. 先做 base-only / reduced 口径 replay
3. 再做 1 轮 reduced SFT
4. 重点看它能不能在干净前提下压过未训练基座
