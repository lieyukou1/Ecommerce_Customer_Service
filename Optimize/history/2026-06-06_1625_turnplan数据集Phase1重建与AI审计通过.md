# 2026-06-06 16:25 TurnPlan 数据集 Phase 1 重建与 AI 审计通过

## 本轮目标

- 重建 `Material/Datasets/turnplan-phase1` 的 Phase 1 数据集生成链
- 解决上一版被审计指出的高重复、覆盖缺口、合同说明不清、多样性不足问题
- 保留后续从数据库历史对话抽取 `history-backed` 样本的能力

## 为什么现在做

- 上一版 450 条样本里存在大量重复，真实有效样本密度很低，已经不具备训练价值
- 用户已明确要求：先修数据集质量，再做 AI 评估，再做人工抽检与真实手动对话，最后再抽取历史对话
- 这一步如果不推倒重做，后面不管是微调还是面试展示都会建立在假数据基线上

## 实际改动

1. 重写数据集脚本链：
   - `build_dataset.py`
   - `validate_dataset.py`
   - `export_sft.py`
   - `audit_dataset.py`
   - `metrics.py`
   - `dataset_factory.py`
   - `dataset_contract.py`
2. 把生成策略改成“模板驱动 + 配额驱动 + 明确合同驱动”，不再沿用旧的低多样性拼接逻辑。
3. 为高风险桶补了更强的多样化生成：
   - `service_item_knowledge`
   - `object_context_followup`
   - `task_interrupt_resume_cancel`
   - `work_order_business_urge`
   - `work_order_business_complaint`
   - `active_task_slot_fill`
4. 把 AI 审计门禁显式化，要求同时检查：
   - 精确重复对
   - Flow 覆盖
   - Knowledge intent 覆盖
   - history 多样性
   - `active_system_task / paused_tasks / multi-slot` 覆盖
   - 训练 system prompt 中的协议合同说明
5. 保留 `scripts/extract_history_backed.py`，继续支持：
   - `--from-db`
   - `--input-jsonl`

## 回归结果

- `build_dataset.py`：通过
- `validate_dataset.py`：通过
- `export_sft.py`：通过
- `audit_dataset.py`：通过

关键结果：
- `450 train + 80 val`
- 全量 `530` 条样本
- 全量唯一 `input + label` 对：`530`
- 精确重复对：`0`
- Flow 白名单覆盖：`8 / 8`
- Knowledge intent 白名单覆盖：`8 / 8`
- 唯一 `user_message`：`513`
- 唯一 `history`：`110`

审计产物：
- `Material/Datasets/turnplan-phase1/reports/ai_audit.json`
- `Material/Datasets/turnplan-phase1/reports/ai_audit.md`

## 未完成项

- 还没有进入人工抽检
- 还没有做用户真实手动对话采样
- 还没有把真实历史对话抽取成 `history-backed` 正式样本

## 下一步优先级

1. 用户先做人工抽检
2. 人工抽检通过后，用户做真实手动对话
3. 对真实对话与现有状态数据做抽取、清洗、整理
4. 把 `history-backed` 样本并入同一 canonical 结构，进入 Phase 2
