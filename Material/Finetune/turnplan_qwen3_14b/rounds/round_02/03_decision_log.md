# round_02 Decision Log

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/00_run_manifest.md)
- 问题分析: [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/02_problem_analysis.md)

## 本轮采纳的解释

### 1. round 2 的收益是真实但有限

采纳理由:
- `task_command_family_accuracy` 确实回升
- `protocol_gate_pass_rate` 也确实回升
- `all_null` 噪声已经不再污染结论

结论:
- round 2 不是无效实验
- 但还远不足以晋级

### 2. 当前主矛盾仍是 `task vs knowledge` 边界教学不足

采纳理由:
- 18 条真实失败里, 11 条集中在 `work_order_read_only_task`
- 这些失败绝大多数不是 flow 错, 而是直接落错轨

结论:
- 下一轮要优先扩的是 read-only 对照样本
- 不是大盘乱补, 也不是先补 flow 长尾

### 3. `active_task_slot_fill` 仍需继续补 active-context 样本

采纳理由:
- 失败数从 3 条降到 2 条, 但仍有短句补槽被打回 `knowledge/all_null`

结论:
- 下一轮保留这一块的小范围增强
- 重点是“短句 + 已有 active_task/active_system_task”组合

### 4. `cancel_flow vs exit_runtime` 还需要成对边界样本

采纳理由:
- 两条典型失败仍是 `cancel_flow -> directive.exit_runtime`

结论:
- 继续补成对样本
- 暂不靠拉长 prompt 解决

## 本轮明确否决的解释

### 1. 否决“再大幅改学习率就能解决主问题”

否决理由:
- LR 下降后, 主要指标只是小幅改善
- read-only 主失败桶几乎没动

### 2. 否决“现在就大改整套数据集”

否决理由:
- 用户已经明确不希望再做一次大规模语言层返工
- 当前数据的 schema、自然度和审计链路已经稳定
- 这时更合理的是精确补强, 不是推倒重来

### 3. 否决“用 prompt 负向列举强写 read-only 不属于 knowledge”

否决理由:
- 这一类规则容易被 14B 过度泛化
- 更稳的是让相似句子在不同 runtime context 下出现不同 label, 靠数据教边界

## round_02 晋级结论

- round_02 candidate **不晋级**
- 蓝版本继续保留远程现网 baseline
- 本地候选可以作为对照参考, 但不作为当前最佳方案
- 并且: **不直接进入 round_03 训练**

## 当前锁定的下一步方向

1. 保留 round 2 的评测口径修正
2. 先进入系统性诊断阶段, 不直接开新训练轮次
3. 用同口径重跑未训练基座
4. 抽 `work_order_read_only_task` 的“基座对 / 微调错”反例
5. 跑训练集回放, 判断候选是否连训练分布都未压过基座
6. 在诊断完成前, 不在 round 2 adapter 上继续补训

## 诊断后新增收口

诊断结果已经支持下面这条更强的判断:

- 当前阶段的主问题更像是“任务定义 / 标签边界 / SFT 塑形方式”不匹配
- 不是简单的“再补几条样本”或“再降一点学习率”就会自然解决
