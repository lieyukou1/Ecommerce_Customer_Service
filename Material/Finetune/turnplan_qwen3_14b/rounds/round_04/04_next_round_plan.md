# round_04 Next Round Plan

## 当前状态

协议兼容重构、联合审计、安全导出、reduced triage、targeted repair、bucket rebuild 都已经完成。

当前已经有一版真正可用的 reduced 候选集：

- [reduced_round04_candidate_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_candidate_v1/summary.md)
- total `264`
- `sft_ready_pass_rate = 1.0`
- `duplicate_pairs = 0`

口径上把这版写死为：

- **validation-oriented training set**
- 目标是验证方向，不是直接产出最终上线模型
- 下一阶段若验证成立，再扩成 **production-oriented expansion set**

下一步不再是继续修数据，而是进入一次受控验证。

## 下一步固定顺序

1. 用 `reduced_round04_candidate_v1` 跑未训练 `Qwen3-14B` baseline
2. 固定 reduced 口径评测指标
3. 启动 1 轮 reduced SFT
4. 跑 runtime replay / scenario replay
5. 对比：
   - 未训练本地基座
   - reduced SFT 候选
6. 再决定是否进入下一轮修正

## 下一步不改的东西

- 不改最终 `TurnPlan JSON` 合同
- 不加第二次 Planner LLM 调用
- 不撤掉 runtime `read_only` 分流层
- 不为了追求数字放宽联合审计门槛

## 下一步主看指标

不再主看笼统的 `top_level_track_accuracy`，主看：

1. `task_command_family_accuracy`
2. `active_task_slot_fill` bucket accuracy
3. `ambiguous_all_null` bucket accuracy
4. `task_interrupt_resume_cancel` bucket accuracy
5. `directive_exit_runtime` bucket accuracy
6. `slot_fill_exact_match`
7. `protocol_gate_pass_rate`

同时保留观察：

- `knowledge_false_positive_rate`
- 高损失 read-only system success

## 晋级门槛

reduced 候选只有在下面条件同时满足时才算成立：

1. 主 bucket 至少有两项明显优于未训练基座
2. `task_command_family_accuracy` 不回退
3. runtime replay 不出现新的结构性副作用
4. 高损失 read-only system success 不明显回退

## 若仍失败，下一步怎么走

如果这轮 reduced SFT 仍压不过未训练基座，不再优先怀疑“明显脏数据”。

下一步要重点回答的是：

1. 失败是否集中在某个剩余机制：
   - 短句补槽
   - clarify trigger
   - cancel / exit 边界
2. unified Planner SFT 的监督空间是否仍然和自然语义存在残余张力
3. 是继续增强对比样本，还是把某一类判断再从训练目标里单独抽出来
