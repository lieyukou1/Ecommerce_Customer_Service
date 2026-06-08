# TurnPlan 微调全链路复盘报告

- 最后更新：2026-06-08
- 文档定位：面向课程验收与项目复盘的正式主报告
- 上级入口：[turnplan_finetune_master_report.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/turnplan_finetune_master_report.md)
- 配套附录：[23_TurnPlan微调证据与轮次附录.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/23_TurnPlan微调证据与轮次附录.md)

## 1. 项目背景与任务定义

本项目原始目标，是让物业客服系统中的 LLM 承担“结构化决策”角色，而不是只负责润色回复。系统希望模型在多轮对话里综合以下信息：

- 当前用户消息
- 对话历史
- 当前聚焦对象 `focused_object`
- 运行时状态 `runtime_state`
- 已激活任务 `active_task / active_system_task`

然后输出统一的 `TurnPlan JSON`，驱动后端进入正确的业务流程。

这次微调之所以选择 `TurnPlan`，是因为它看上去同时满足三个条件：

1. 输出协议固定，适合监督微调。
2. 好坏可通过离线 replay 检查，不必只看主观回复质量。
3. 一旦学稳，收益会直接落在客服系统主链上，而不是只体现在话术更自然。

但这也意味着，这不是一个普通的“单轮意图分类 + 槽位抽取”任务。它本质上是一个状态感知的多轮决策任务：同一句用户话，在不同状态下可能对应不同的决策。

## 2. 协议设计与初始任务假设

本项目的 LLM 最终输出合同固定为 `TurnPlan JSON`，顶层只允许四类主轨道：

- `task`
- `knowledge`
- `chitchat`
- `directive`

若当前轮既不应启动任务，也不应进入知识问答、闲聊或运行时控制，则四个字段全为 `null`，项目内部把这种情况称为 `all_null`。

初始设计的核心假设是：只要给模型足够清晰的上下文，它就能同时学会两件事：

1. 用户在语言层面“想要什么”
2. 项目在协议层面“这件事应该走哪条内部通道”

后续实验表明，这两个判断并不总是天然一致。最典型的张力集中在 `read_only` 场景：

- 用户语言层面是在“查询”某个信息
- 系统协议层面却可能要求它走只读 `task flow`

例如“这单现在什么状态”“帮我看一下处理进度”“我有哪些工单”，在用户语言上都更像查询，但在系统里又要求模型区分：

- 是 `knowledge`
- 还是只读 `task`
- 是否需要带上当前对象 ID

这条边界后来被证明是整个微调链路最核心的结构性张力之一。

## 3. 数据收集、数据集设计与第一次乐观假设

### 3.1 初始设计

Phase 1 canonical 数据集最初按统一 `TurnPlan` 协议设计，规模为：

- train：`450`
- val：`80`

数据集试图覆盖 10 个 bucket，既包括：

- 业务办理类样本
- 多轮 continuation 与 slot fill
- 中断 / 恢复 / 取消 / 退出
- 模糊表达与 `all_null`
- 闲聊与知识问答

也包括对象上下文、长历史、运行时状态等字段。

### 3.2 第一次乐观假设

项目最初默认相信的是：

- 只要 schema 合理，标签逻辑正确，SFT 就能学进去；
- 只要把 `user_message` 写得更像真人，模型就会更容易泛化；
- 只要补充几个 hard case，统一 Planner SFT 就能逐步压过 base。

这个判断后来被证明过于乐观。问题不只在语言自然度，还在于：

- 样本是否真的形成了有效监督信号；
- 同一句话在不同状态下的标签差异，是否被设计成了模型可学的对照；
- 输入字段之间是否属于同一条合理时间线。

## 4. 数据审计升级过程

### 4.1 第一阶段：语言自然度审计

最早发现的问题，是训练数据存在明显 AI 痕迹，主要包括：

- 模板拼接残留，例如“比如”没有清干净；
- 用户自我标注意图，例如“我是在补催办原因”；
- 机械枚举、排列组合式生成；
- 系统内部视角语言混入用户话术。

为此，数据集进行了较大规模的语言层重写，并引入多模型改写，避免单一模型风格污染。

### 4.2 第二阶段：多模型重写与自然表达替换

在这一步里，原有 label 体系和 flow / intent 体系被保留，但语言层进行了大规模替换。核心原则变成：

> 不补模板式提示，不让用户替系统说明自己在做什么，只保留真实用户可能会说的话。

这一阶段解决了很多显眼问题，但仍然不够。

### 4.3 第三阶段：从“语言自然”升级到“联合审计”

后续进一步发现，只看 `user_message` 自然不自然是不够的。真正危险的是“伪上下文”进入 SFT：

- history 与当前标签冲突；
- `active_task` 明明为空，却把当前轮标成 continuation；
- `focused_object` 与当前用户指代对象不一致；
- gold slots 在输入里没有来源；
- 输入字段本身就在泄漏答案。

因此后续审计升级为“语言 + 时间线 + 状态 + 对象 + 槽位”的联合审计。到 [round_04/01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/01_outputs.md) 时，核心审计指标已经变成：

- `sft_ready_pass_rate = 0.8358`
- `language_naturalness_pass_rate = 0.8943`
- `history_state_consistency_pass_rate = 0.9340`
- `object_slot_consistency_pass_rate = 0.9925`

这说明后期的工作重点，已经从“让句子像真人”转向“让整条样本时间线自洽”。

## 5. 训练框架、资源约束与实验闭环设计

### 5.1 框架选择

本项目最终固定采用：

- 基座模型：`Qwen3-14B`
- 训练方式：`QLoRA`
- 训练框架：`LLaMA-Factory`
- 推理框架：`vLLM`

原因并不神秘：

- 14B 对中文结构化任务有基本能力上限；
- QLoRA 适合单机 48GB 显存；
- `LLaMA-Factory` 已覆盖本项目所需训练形态；
- `vLLM` 与当前后端的 OpenAI-compatible 接法兼容。

### 5.2 资源约束

训练主要依赖单机 AutoDL 4090 环境：

- `RTX 4090 48GB`
- `25 vCPU`
- `92GB RAM`
- 数据盘约 `223GB`

这个约束直接影响了项目策略：

- 不能走全量微调；
- 不能把实验规模铺得过大；
- 必须让训练、导出、评测、artifact 落盘形成闭环，而不是依赖临时环境记忆。

### 5.3 实验闭环

本项目不是“训完看 loss”就结束，而是设计成四层验收：

1. 离线指标对比
2. `protocol gate`
3. runtime replay
4. smoke + 人工抽检

这里尤其重要的一点是 baseline 设计。项目始终保留三类对照：

- 远程现网 baseline
- 本地未训练 `Qwen3-14B`
- 本地微调 candidate

如果没有这三类基线，就无法回答：

- 当前产品实际表现如何；
- 基座本身已经有多强；
- 微调到底带来了净收益，还是只是扰动。

## 6. 指标体系设计与指标含义说明

### 6.1 为什么不能只看一个总准确率

`top_level_track_accuracy` 只能回答一个很粗的问题：模型把当前轮大致分到了哪条轨道。

它不能回答：

- `task` 里命令族是否正确；
- flow 是否选对；
- slot 是否补对；
- 输出虽然看上去对，下游是否能过 gate；
- 高损失只读场景是否真的能落到正确执行链。

因此，从一开始就只看一个“总准确率”会产生明显误导。一个候选模型可能：

- 顶层轨道路由涨了；
- 但 flow 和 slot 更差；
- 最终系统行为反而退化。

这正是后期多轮实验不断遇到的现象。

### 6.2 本项目固定主指标及其意义

#### `top_level_track_accuracy`

- 测什么：顶层 `task / knowledge / chitchat / directive / all_null` 是否匹配。
- 为什么重要：它是最直观的路由正确率。
- 误导点：它无法说明 `task` 内部命令是否对。
- 指标性质：更偏语言理解指标。

#### `directive_accuracy`

- 测什么：`directive` 类样本的动作是否正确。
- 为什么重要：退出、结束当前上下文这类动作一旦错，用户体验会直接受损。
- 误导点：该指标通常样本量不大，不能代表整体任务。
- 指标性质：语言理解 + 运行时控制边界指标。

#### `all_null_accuracy`

- 测什么：该轮是否正确保持四轨全空。
- 为什么重要：它衡量模型是否能在模糊或不应冒进的场景下克制。
- 误导点：单独追高会让模型变得过度保守。
- 指标性质：语言理解指标。

#### `knowledge_intent_accuracy`

- 测什么：知识轨道意图是否匹配。
- 为什么重要：它能观察模型在非任务办理类场景下是否稳定。
- 误导点：知识类样本往往更容易，容易掩盖任务类退化。
- 指标性质：语言理解指标。

#### `task_command_family_accuracy`

- 测什么：`task` 轨道下，命令族是否正确，例如 `start_flow / set_slots / cancel_flow / resume_flow`。
- 为什么重要：这是任务办理类判断的核心，比“是否进入 task”更接近真实可执行性。
- 误导点：命令族对了，不代表 flow 对了。
- 指标性质：系统可执行性指标。

#### `flow_selection_accuracy`

- 测什么：需要选 flow 的任务类样本里，flow 是否选对。
- 为什么重要：错误 flow 会直接把用户送进错误业务链。
- 误导点：在 continuation-only 样本中，该指标不总能覆盖核心难点。
- 指标性质：系统可执行性指标。

#### `slot_fill_exact_match`

- 测什么：需要补槽位的样本里，抽取和合并后的 slots 是否完全匹配 gold。
- 为什么重要：多轮 continuation 的真正难点经常体现在这里。
- 误导点：该指标严格且稀疏，容易低，但低不一定代表整体都坏。
- 指标性质：系统可执行性指标。

#### `json_valid_rate`

- 测什么：模型输出是否是合法 JSON。
- 为什么重要：这是所有后续评测的第一层门槛。
- 误导点：格式合法不等于业务正确。
- 指标性质：格式合法性指标。

#### `protocol_gate_pass_rate`

- 测什么：模型输出是否通过协议闸门。
- 为什么重要：它反映结果是否满足系统协议约束。
- 误导点：有些 `all_null -> clarify fallback` 场景若按旧口径算失败，会污染判断。
- 指标性质：系统可执行性指标。

#### `adjusted_protocol_gate_pass_rate`

- 测什么：把“符合预期的 clarify fallback”从失败里剥离后，重新计算的有效 gate 通过率。
- 为什么重要：它比原始 gate 指标更接近真实系统可用性。
- 误导点：仍然不能代替 flow 和 slot 层判断。
- 指标性质：系统可执行性指标。

#### `knowledge_false_positive_rate`

- 测什么：gold 为 `task` 的样本中，被误打成 `knowledge` 的比例。
- 为什么重要：它是观察 `task -> knowledge` 漂移的核心指标。
- 误导点：只看这一项会忽略 `task -> all_null` 的保守漂移。
- 指标性质：结构性误差指标。

#### `high_loss_read_only_system_success_rate`

- 测什么：高损失只读场景在 runtime 层面是否成功命中正确执行链。
- 为什么重要：这是 read-only 重定义后必须新增的系统级指标。
- 误导点：它不反映统一 Planner SFT 本身是否学会了纯语义边界。
- 指标性质：系统成功率指标。

### 6.3 指标之间的层级关系

本项目最终把指标分成五层：

1. **格式合法性**
   - `json_valid_rate`
2. **顶层轨道路由**
   - `top_level_track_accuracy`
   - `directive_accuracy`
   - `all_null_accuracy`
   - `knowledge_intent_accuracy`
3. **任务命令与 flow 选择**
   - `task_command_family_accuracy`
   - `flow_selection_accuracy`
4. **槽位精度**
   - `slot_fill_exact_match`
5. **runtime / system 成功率**
   - `protocol_gate_pass_rate`
   - `adjusted_protocol_gate_pass_rate`
   - `high_loss_read_only_system_success_rate`

这个分层意味着：上层指标好，不代表下层一定好。真正能用于晋级判断的，是中下层指标的综合结果。

### 6.4 本项目为什么最终更信哪些指标

后期项目不再让 `top_level_track_accuracy` 单独主导结论，原因很直接：

- 顶层轨道对了，命令族仍可能错；
- 命令族对了，flow 仍可能错；
- flow 对了，slot 仍可能错；
- 全部看起来都还行，runtime 仍可能过不了。

因此后期更重视：

- `task_command_family_accuracy`
- `flow_selection_accuracy`
- `adjusted_protocol_gate_pass_rate`

而在 read-only 重定义后，又必须补看：

- `high_loss_read_only_system_success_rate`

因为此时项目不再强求统一 SFT 去硬学所有高损失只读边界，而是允许 runtime 承担一部分执行分流职责。

## 7. 实验结果与 Base vs SFT 多轮对比

### 7.1 round_01：统一 Planner SFT 首轮试跑

关键变化：

- 首次完成 `Qwen3-14B + QLoRA` 训练闭环；
- 拿到 runtime failures 导出；
- 建立 base、remote baseline、candidate 的对照。

核心结果：

- `top_level_track_accuracy = 0.7750`
- `task_command_family_accuracy = 0.5349`
- `flow_selection_accuracy = 0.5161`
- `protocol_gate_pass_rate = 0.8375`

相对 base 的判断：

- 未训练 base no-think 的 `top_level_track_accuracy = 0.7625`，candidate 仅略高；
- 但 `task_command_family_accuracy` 明显更差；
- 高失败 bucket 集中在 `work_order_read_only_task`。

这轮支持的判断是：统一 SFT 没有带来明确净收益，结构性问题先暴露在只读边界。

### 7.2 round_02：降学习率与小修样本后的二次验证

关键变化：

- 调整训练配置；
- 补了一批针对性样本；
- 补 smoke 和系统诊断。

核心结果：

- `top_level_track_accuracy = 0.7750`
- `task_command_family_accuracy = 0.5814`
- `flow_selection_accuracy = 0.5161`
- `adjusted_protocol_gate_pass_rate = 0.9125`

相对 base 的判断：

- 相比 round_01 略有修复；
- 但仍未压过未训练 base；
- `work_order_read_only_task` 仍是最大失败桶。

这轮支持的判断是：问题不像纯超参问题，更像任务定义与监督空间不匹配。

### 7.3 round_03：重定义 + reduced SFT 首次验证

关键变化：

- 先做 read-only 重定义；
- 让高损失 read-only 先由 runtime 吸收；
- 在 reduced 数据集上做一轮 no-thinking 对照。

核心结果：

- 高损失 `read_only` 的 system success 在验证集达到 `1.0000`；
- candidate 在 `ambiguous_all_null` 上显著优于 base；
- 但在 `active_task_slot_fill`、`work_order_business_complaint` 等任务类 bucket 上仍退化。

典型 no-thinking 指标对比：

| 指标 | base | reduced candidate |
| --- | ---: | ---: |
| `top_level_track_accuracy` | 0.7262 | 0.8214 |
| `task_command_family_accuracy` | 0.7222 | 0.6667 |
| `flow_selection_accuracy` | 0.8621 | 0.8276 |
| `slot_fill_exact_match` | 0.2093 | 0.1860 |
| `adjusted_protocol_gate_pass_rate` | 0.9881 | 0.9524 |

这轮支持的判断是：重定义能收掉一部分训练压力，但 reduced SFT 的净收益仍然不稳定。

### 7.4 round_04：不训练，先清协议与清数据

关键变化：

- `TurnPlanNormalizer -> ReadOnlyResolver` 职责切开；
- 高损失 read-only rewrite 下沉到 runtime 正式层；
- 做联合审计和安全导出；
- 组装 `reduced_round04_candidate_v1`。

核心结果：

- safe export：`train = 374`，`val = 69`
- reduced candidate：`264` 条
- `sft_ready_pass_rate = 1.0`
- `duplicate_pairs = 0`
- `unsafe_records = 0`

这轮不提供模型胜负结论，但提供了非常重要的条件清理：后续实验终于能在“更干净的监督输入”上比较 base 与 candidate。

### 7.5 round_05：干净 reduced 流水线首次正式训练

关键变化：

- 在 `reduced_round04_candidate_v1` 上做正式 reduced SFT；
- 跑通 adapter merge、vLLM serving、runtime replay。

核心结果：

| 指标 | base | candidate |
| --- | ---: | ---: |
| `top_level_track_accuracy` | 0.8205 | 0.7692 |
| `task_command_family_accuracy` | 0.7778 | 0.7407 |
| `flow_selection_accuracy` | 0.9333 | 0.8667 |
| `slot_fill_exact_match` | 0.2174 | 0.2174 |
| `adjusted_protocol_gate_pass_rate` | 0.9231 | 0.8718 |

这轮支持的判断是：

- 训练流程本身没有坏；
- 但 supervision signal 仍没能把 candidate 推到 base 之上；
- 候选模型略微更保守，却为此丢掉了真实任务 continuation 的判断。

### 7.6 round_06：最干净条件下的对照验证

关键变化：

- 真正使用 minimized schema export；
- 补入显式 same-utterance contrast groups；
- 再做一轮 reduced SFT。

核心结果：

| 指标 | base | candidate |
| --- | ---: | ---: |
| `top_level_track_accuracy` | 0.8205 | 0.7692 |
| `task_command_family_accuracy` | 0.7778 | 0.7407 |
| `flow_selection_accuracy` | 0.9333 | 0.8000 |
| `slot_fill_exact_match` | 0.2174 | 0.2174 |
| `adjusted_protocol_gate_pass_rate` | 0.9231 | 0.8462 |

这轮支持的判断最关键：

- “旧 export 泄漏”不是主因；
- “只是缺少 hard contrast rows”也不是主因；
- 即使在更干净的输入和更明确的对照下，candidate 仍未压过 base。

### 7.7 Base 与 SFT 候选的差距分析

综合多轮结果，可以看到一个稳定模式：

#### 1. base 在核心任务判断上更稳

尤其在后期 reduced 口径下，base 在以下指标上持续领先：

- `task_command_family_accuracy`
- `flow_selection_accuracy`
- `adjusted_protocol_gate_pass_rate`

这说明 base 在“任务 continuation / 任务切换 / 动作选择”上已经具备了不错的自然语义先验。

#### 2. SFT 不是完全无收益，但收益集中在局部

最明显的正收益出现在：

- `ambiguous_all_null`

也就是说，SFT 能教模型更克制，减少一部分不该启动任务的冒进判断。

#### 3. 但这种克制有副作用

同一轮里，candidate 又经常把真实 continuation 错打成：

- `all_null`
- `exit_runtime`

这说明 LoRA 更新没有只“补上缺失规则”，而是同时扰动了 base 原本已有的判断路径。

#### 4. 训练 loss 下降，不代表系统表现提升

多个轮次的训练 loss、eval loss 都较低，但 candidate 在 runtime replay 中仍落后于 base。这再次证明：

- SFT loss 优化的是训练目标拟合；
- 但本项目真正关心的是系统可执行行为；
- 如果训练目标本身和系统真实难点没有稳定对齐，loss 好看也不能说明可上线。

#### 5. 指标局部上涨，也不构成晋级依据

即使某一轮中：

- `top_level_track_accuracy` 上升；
- 或某个 bucket 局部改善；

只要：

- `task_command_family_accuracy`
- `flow_selection_accuracy`
- `adjusted_protocol_gate_pass_rate`

没有形成净收益，就不能认为模型已经更好。

## 8. 根因分析与被证伪的解释

### 8.1 已经被证伪的解释

#### 只是 export 泄漏导致失败

这在 round_06 已被排除。最小 schema export 与旧泄漏被清掉后，candidate 仍然落后于 base。

#### 只是缺少几组 contrast rows

round_06 显式加入了 targeted contrast groups，但 candidate 仍未形成净收益。

#### 只是学习率设置不对

从 round_01 到 round_02 已经做过学习率与小修样本调整，结果并未转正，说明超参不是主因。

### 8.2 基本成立的解释

#### supervision 目标与 base 语义先验之间存在张力

base 已经知道很多“自然语义上该怎么理解”的东西，而项目协议要求模型进一步区分一条更人为的边界，例如：

- 查询类语句到底是 `knowledge` 还是只读 `task`
- 短句到底是 standalone query 还是 active task continuation

#### 小规模 SFT 没能稳定强化协议边界，反而扰动了 base 已有判断

这正是多轮实验反复出现的模式：candidate 稍微更“守规矩”，但真实 continuation 与 switch 判断反而变差。

#### 难点集中在状态依赖型 continuation 与动作选择

系统并没有在所有维度都失败：

- `directive_exit_runtime` 通常不难；
- `work_order_business_urge` 也相对稳定；

真正困难的是：

- `active_task_slot_fill`
- `task_interrupt_resume_cancel`
- `work_order_business_complaint`

这些场景都高度依赖运行时状态和动作边界。

### 8.3 仍需谨慎的判断

#### 这是否说明统一 Planner SFT 完全不可行

当前证据只能说明：在现有任务定义、数据规模、资源周期下，它没有形成净收益。不能据此直接推出“永远不可行”。

#### 还是说明当前组合不适合这样训

更谨慎也更合理的判断是：

- 统一 Planner SFT 的目标空间过于紧张；
- 数据量不大；
- base 先验较强；
- runtime 协议边界又带有人为性；

这组条件叠在一起，使当前路线的收益非常难稳定压过 base。

## 9. 优化路径、下一轮方向与最终转向

### 9.1 runtime 吸收 read-only 带来的真实收益

`read_only` 被 runtime 吸收之后，至少带来了三点真实收益：

1. 高损失只读场景不再要求统一 SFT 主任务硬学全部边界；
2. 高风险业务正确性先由系统层保证；
3. 训练目标收缩后，实验结论更干净。

这不是“偷懒绕过 LLM”，而是把系统设计里本来就不适合硬塞给小规模 SFT 的部分收回运行层。

### 9.2 哪些训练压力已经被收掉

已经明显下降的训练压力主要是：

- 工单列表查询
- 服务项目列表查询
- 工单状态查询
- 服务进度跟踪
- 服务项目详情查询

这些场景目前不再构成统一 Planner SFT 的主学习负担。

### 9.3 哪些压力仍然留在统一 SFT 主任务里

真正仍然困难的部分是：

- active task continuation
- deictic 短句补槽
- cancel / exit / switch 的动作区分
- 保守 fallback 与真实任务启动之间的平衡

这也是 why reduced 后仍然没有自然转正。

### 9.4 为什么短期不再继续赌统一 Planner SFT

到 round_06 为止，项目已经排除了多个“简单解释”。继续同类训练的边际收益已经很低，而时间成本很高。

因此短期主交付不再继续押统一 Planner SFT，理由不是“前面白做了”，而是：

- 现在已经知道这条线的主要瓶颈是什么；
- 继续同配方加料，不再是证据驱动的决定；
- 项目需要一个能在有限时间内产生可见效果的方向。

所以后续转向更可见的功能交付，是对现状更诚实的工程选择。

## 10. 结论、项目价值与方法论收获

### 10.1 项目结论

本次 TurnPlan 微调没有产出一个能够稳定压过 base、可直接晋级上线的统一 Planner 候选模型。

这不是一个“成功上线的 SFT 项目”，但它也绝不是“只留下心得体会”的空项目。它真正产出的，是一套经过失败验证过的方法论和判断边界。

### 10.2 真实得到的东西

本项目至少明确了以下几件事：

1. 数据自然度不等于监督目标可学。
2. 小规模 SFT 不会自动学会带有人为协议边界的系统规则。
3. 评测不能只看总准确率，必须看任务命令、flow、slot 与 runtime 成功率。
4. runtime 结构、训练目标、评测口径必须协同设计，不能各自独立优化。
5. 当统一主任务过重时，先收掉高损失边界，再验证剩余目标，结论会更干净。

### 10.3 如果重来一次

如果从头再做一次，本项目更合理的起点会是：

1. 先明确哪些能力是自然语义问题，哪些是系统协议问题；
2. 对状态依赖型 continuation 单独设计更强对照；
3. 更早建立“语言审计 + 联合审计”的双层验收；
4. 更早把高损失只读边界放到 runtime 正式分流层；
5. 选择一个更窄、更可学、更容易形成净收益的微调子任务做首个闭环。

### 10.4 项目后续建议

若继续沿 AI 方向推进，更稳妥的思路不是继续强押统一 Planner SFT，而是：

- 把统一 Planner 看作长期目标；
- 把短期可交付目标放在更窄任务的 AI 辅助模块上；
- 让运行层承担本就更适合由系统保证的高损失边界。

这次微调虽然没有直接训出候选模型，但它把“什么值得继续训、什么不该继续硬训”讲清楚了。这一点，本身就是后续所有决策的基础。
