# round_03 Problem Analysis

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/00_run_manifest.md)
- 结果摘要: [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/01_outputs.md)

## 本轮分析目标

这一轮分成两段分析:

1. 高损失 `read-only` 是否已经从“模型硬学边界”转成“runtime 保业务正确”
2. reduced SFT 在新任务定义下，到底有没有给基座带来净收益
3. 如果没有净收益，问题更像服务形态、数据配比，还是训练超参

## 先看结论

- 高损失 `read-only` 的 runtime 吸收逻辑已经证明有效
- reduced SFT 真正带来的主要增益是 `ambiguous_all_null`
- 但 reduced SFT 同时把 `active_task_slot_fill` 和一部分业务 task 打得更保守
- 默认 reasoning 服务会额外制造空 `content` / 非 JSON 输出，必须先剥离
- 所以当前主矛盾已经变成:
  - `ambiguous_all_null` 提升是否值得
  - `active_task_slot_fill` / 业务投诉切换 的回退如何修

## phase_a: 高损失 read-only 吸收收益

### 1. 验证集已经全救回

- `high_loss_read_only_metrics.count = 14`
- `system_success_rate = 1.0000`
- `list_query_success_rate = 1.0000`
- `work_order_runtime_success_rate = 1.0000`
- `service_item_detail_success_rate = 1.0000`

解释:

- 即使模型原始输出还会把部分只读问题打成 `knowledge`
- runtime 已经把“业务后果最重”的只读场景先吸收回正确执行链
- 这条线不该再回到统一 SFT 的主学习负担里

### 2. 训练集只剩少量尾巴

- 训练集 `71` 条高损失样本里，`system_success_rate = 0.9437`
- 尾巴主要还剩服务项目详情吸收偏保守
- 但这已经是 runtime 尾修问题，不再是统一 SFT 的主矛盾

## phase_b: reduced SFT 的真实收益与代价

### 1. 默认 reasoning 服务会污染评测

现象:

- base / candidate 在默认 Qwen3 服务方式下都会出现空 `content`
- candidate 受影响更大，`json_valid_rate` 一度掉到 `0.8929`

判断:

- 这不是训练本身的标签错
- 而是 Qwen3 reasoning / content 交互形态和 TurnPlan JSON 任务天然冲突
- 后续所有 TurnPlan 评测必须默认走 `no-thinking`

### 2. `ambiguous_all_null` 提升是真收益

同口径 `no-thinking val`:

- base: `0.2000`
- candidate: `0.8500`

这不是小抖动，是实打实的主任务提升。

### 3. 但 candidate 变得过于保守，主要伤在 active context

同口径 `no-thinking val` 的 5 个净回退样本里:

- `3` 条在 `active_task_slot_fill`
- `1` 条在 `work_order_business_complaint`
- `1` 条在 `task_interrupt_resume_cancel`

典型表现:

- 明明已有 `active_task` / `active_system_task`
- 用户只是在补当前槽位或从催办切投诉
- candidate 却退回 `all_null` 或 `knowledge`

关键证据:

- `active_task_slot_fill.track_accuracy`
  - base `0.9000`
  - candidate `0.7500`
- `active_task_slot_fill.track_accuracy` 在 **candidate train** 里也只有 `0.7671`

这说明它不是“只在验证集泛化丢了”，而是训练目标本身把模型往保守方向拉偏了。

### 4. `task_interrupt_resume_cancel` 还没有真正被训稳

同口径 `no-thinking val`:

- base `0.7500`
- candidate `0.7000`

这里不是大崩，但说明 reduced SFT 的收益还没有稳定覆盖到“活跃任务切换”这块。

### 5. `adjusted_protocol_gate_pass_rate` 仍是 base 更高

- base `0.9881`
- candidate `0.9524`

所以当前不能只拿 `top_level_track_accuracy` 或 `all_null_accuracy` 就宣布晋级。

## 当前最支持的解释

### 1. 不是 schema 问题

- schema 没变
- runtime / parser / gate 也都打通了
- 同一套 schema 下，bucket 之间出现了清晰的此消彼长

### 2. 更像是目标桶之间的学习拉扯

证据:

- `ambiguous_all_null` 大幅提升
- `active_task_slot_fill` 和部分业务 task 同时回退
- 训练集上也复现这个方向

这比“单纯超参没调好”更像数据配比和边界对比信号的问题。

### 3. 不是继续补 read-only 就能救

- 高损失 `read-only` 已经被 runtime 接住
- 再补这块只会把注意力从真正的 reduced 主矛盾上拉走

## 当前不支持的解释

### 1. “这轮已经可以直接晋级上线”

不支持。

因为:

- candidate 虽然终于在 `top_level_track_accuracy` 上压过 base
- 但它还没有在整体业务风险上形成净胜

### 2. “下一轮先调 prompt 规则就行”

不支持。

当前更强的证据仍指向:

- active context 的对比样本不够扎实
- `ambiguous_all_null` 与 active slot fill 之间的权重拉扯没有处理好

## 归纳判断

这一轮真正落下来的判断是:

- 高损失 `read-only` 先交给 runtime 是对的
- reduced SFT 也不是完全无效，它已经在 `ambiguous_all_null` 上证明了价值
- 但当前 reduced 数据集还没有把“模糊表达提升”和“active context 补槽不回退”同时做到
- 下一步该动的是 **targeted dataset repair**，不是 schema 重构
