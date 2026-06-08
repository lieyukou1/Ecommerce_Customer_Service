# round_03 Decision Log

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/00_run_manifest.md)
- 问题分析: [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/02_problem_analysis.md)

## 先行锁定的决策

### 1. 先重定义，不直接沿用 round_02 继续训

采纳理由:

- 连续两轮统一 SFT 没有稳定压过未训练基座
- 当前证据已经足够支持“先立靶子，再决定是否继续射”

### 2. 高损失 `read-only` 先交给 runtime 吸收

采纳理由:

- 这类边界更像内部协议约束，不是强语言规律
- 直接让 14B 用小规模 SFT 去硬背，成本高且收益不稳

### 3. round_03 先做 base-only replay

采纳理由:

- 需要先看新口径下的基座上限
- 如果新主任务下基座已经足够强，就没有继续训的必要

## 本轮新增采纳的解释

### 1. 高损失 `read-only` 先交给 runtime，这条路继续保留

采纳理由:

- 验证集 `14/14` system-level success 全通过
- 训练集尾巴已经明显缩小

结论:

- 不再把这块当成 reduced `round_03` 的主学习负担
- 后续只保留小范围尾巴修正，不回到“让模型硬学全部 read-only 边界”的路线

### 2. reduced SFT 不是白训，但它只在一部分主任务上产生了净收益

采纳理由:

- `ambiguous_all_null` 在 `no-thinking val` 上从 `0.2000 -> 0.8500`
- `top_level_track_accuracy` 也从 `0.7262 -> 0.8214`

结论:

- reduced 方向本身有价值
- 但当前候选还不能直接晋级

### 3. `no-thinking serving` 必须写成固定前置条件

采纳理由:

- 默认 Qwen3 服务方式会引入空 `content` / 非 JSON 自然语言解释
- 这会直接污染 TurnPlan JSON 评测

结论:

- 后续 TurnPlan 评测、对比和人工验收默认都走 `enable_thinking=false`
- 不再拿“带 reasoning 的服务结果”做训练成败判断

### 4. 如果继续训，主靶子要改成“两升一保”

采纳理由:

- `ambiguous_all_null` 的提升已经证明可学
- `active_task_slot_fill` 回退说明当前桶配比或边界对比信号不够
- `task_interrupt_resume_cancel` 也还没有稳定受益

结论:

- 下一步要同时做到:
  - 继续保住 `ambiguous_all_null`
  - 修回 `active_task_slot_fill`
  - 稳住 `task_interrupt_resume_cancel`

### 5. 新阶段不再让 `top_level_track_accuracy` 单独决定去留

采纳理由:

- 这轮高损失业务后果已经被 runtime 救回
- 但 reduced SFT 的净收益仍呈现“有赢有输”

结论:

- 后续评测至少同时看:
  - `active_task_slot_fill`
  - `task_interrupt_resume_cancel`
  - `slot_fill_exact_match`
  - `adjusted_protocol_gate_pass_rate`

## 本轮明确否决的解释

### 1. 否决“高损失 read-only 还是要拉回统一 SFT 主任务”

否决理由:

- runtime 已经证明能先把业务正确性救回来
- 再把它塞回统一 SFT，只会重新把靶子拉歪

### 2. 否决“当前 candidate 已经足够好，直接继续往后推”

否决理由:

- `adjusted_protocol_gate_pass_rate` 仍低于 base
- `active_task_slot_fill` 在 train / val 都掉了
- 这还不是一个能当主候选切流量的状态

### 3. 否决“先靠 prompt 再缝一轮”

否决理由:

- 当前 evidence 更明确指向数据与桶配比
- 先动 prompt 只会把因果搞混

## 当前收口结论

- `round_03` 的前置重定义阶段 **通过**
- `round_03 reduced SFT trial` 已完成，但 **未晋级**
- 下一步优先级已经从“再训一轮看看”收口为“先修 targeted dataset，再用同超参复试”
