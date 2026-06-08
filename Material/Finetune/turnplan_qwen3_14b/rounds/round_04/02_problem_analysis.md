# round_04 Problem Analysis

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/00_run_manifest.md)
- 结果摘要: [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/01_outputs.md)

## 这轮分析目标

这轮不是分析训练输赢，而是先回答三件事：

1. 旧数据里哪些问题已经不该继续让统一 SFT 承担
2. 哪些问题是样本逻辑链本身坏了，不是只改 `user_message` 就能救
3. reduced 下一轮到底应该用什么样的数据再试

## 发现 1：高损失 read-only 的主矛盾已经从“训练问题”转成“runtime 正确性问题”

现象：

- read-only 问法和 knowledge 问法天然接近
- 这类边界如果硬塞给小规模 SFT，会持续和底座自然语义先验打架
- 但业务上它又确实高损失，不能放任错判

本轮结论：

- 这部分先由 runtime 正式分流层吸收是合理的
- reduced round_04 不再把它放回主训练矛盾里

## 发现 2：旧样本的危险点不只在“话不像真人”，更在“字段不在同一时间线”

联合审计表明，之前最危险的是这几类：

- `ambiguous_all_null`：模糊表达里有模板残留，且大量样本没有状态 lead-in
- `directive_exit_runtime`：几乎整桶都缺“当前确实有一段上下文可退出”的 lead-in
- `active_task_slot_fill`：很多补槽句虽然自然，但 `history -> active_task -> 当前补槽` 链条太薄

这说明：

- 只做语言润色不够
- 必须同时修 `history / runtime_state / active_task / focused_object / output`

## 发现 3：safe export 已经证明“不是所有旧数据都该继续喂给 SFT”

canonical 结果：

- total `530`
- safe SFT `443`

说明问题不是规则太严，而是旧数据里本来就混有不该继续训练的样本。

这一步的意义是：

- 后续训练不再默认“样本越多越好”
- 先过联合审计，再谈训练收益

## 发现 4：reduced triage 已经足够指向下一步修复重点

triage 结果非常清楚：

- `keep = 122`
- `targeted_fix = 60`
- `bucket_rebuild = 82`

这意味着下一步不需要全量重做，也不该继续零碎缝补，而是：

- 用 `keep` 做干净底盘
- 单独修 `active_task_slot_fill`
- 整桶重建 `ambiguous_all_null`
- 整桶重建 `directive_exit_runtime`

## 发现 5：新的 reduced candidate 已经把“脏样本”问题压到可控区间

candidate v1 结果：

- total `264`
- `sft_ready_pass_rate = 1.0`
- `language_naturalness_pass_rate = 1.0`
- `history_state_consistency_pass_rate = 1.0`
- `object_slot_consistency_pass_rate = 1.0`
- `duplicate_pairs = 0`

这不代表模型一定会赢，但代表：

- 下一轮如果再输，锅就更不可能是“明显脏数据”了
- 我们终于能更干净地验证“统一 Planner SFT 在这个缩窄任务上到底能不能带来净收益”

## 这轮不支持的解释

### 1. “现在 candidate 干净了，说明训练肯定会赢”

不支持。

原因：

- 数据变干净，解决的是验证前提，不是直接解决模型能力
- 下一轮仍然可能输在任务定义张力、监督强度不足、或 unified SFT 对该混合能力不稳

### 2. “既然 runtime 接住了一部分 read-only，说明统一 SFT 方向错了”

不支持。

原因：

- runtime 只是先接住最不适合硬学的高损失边界
- 统一 SFT 仍然可以验证剩余核心能力：
  - 模糊 task 意图识别
  - active context 槽位补全
  - cancel / resume / exit 边界

## 当前分析收口

这一轮真正得到的，不是一个更高的模型分数，而是一个更干净的验证前提：

- 高损失 read-only 压力被移出主训练矛盾
- 联合审计把伪上下文挡在训练外
- reduced candidate 已经形成

所以下一步终于可以进入：

**拿这版 `reduced_round04_candidate_v1` 去做一次真正有解释力的 reduced SFT 验证。**
