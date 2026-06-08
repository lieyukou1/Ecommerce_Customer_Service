# round_01 Run Manifest

- round_id：`round_01`
- run_name：`qwen3-14b-turnplan-pilot-20260607a`
- 轮次类型：`pilot`
- 基座模型：`Qwen/Qwen3-14B`
- 训练方式：`QLoRA 4-bit`
- 推理框架：`vLLM`
- 训练框架：`LLaMA-Factory`
- 数据集版本：`turnplan-phase1 / exports_llm`
- 轮次目标：验证第一轮本地 14B TurnPlan 微调链路与 runtime 回放结果

## 本轮改动范围

- 样本版本：使用完成语言层重写与审计收口后的 `turnplan-phase1`
- prompt：沿用当前 TurnPlan 合同，不在 system prompt 中追加“task 不属于 knowledge”的负向列举
- 评测口径：本轮仍沿用旧口径，因此 `all_null` 的 protocol gate reject 还混在失败统计里
- 超参：pilot 配置，后续 round 2 才计划把学习率从 `1e-4` 下调到 `5e-5`

## 训练配置摘要

- quantization：`NF4 4-bit`
- compute dtype：`bf16`
- LoRA：
  - `rank=32`
  - `alpha=64`
  - `dropout=0.05`
- sequence length：`2048`
- per-device batch size：`1`
- gradient accumulation：`16`
- learning rate：`1e-4`
- epochs：`3`
- warmup ratio：`0.03`
- seed：pilot 单 seed

## 已知产物

- runtime 原始结果：
  - [qwen3_14b_turnplan_pilot_20260607a_runtime_failures.csv](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_pilot_20260607a_runtime_failures.csv)
  - [qwen3_14b_turnplan_pilot_20260607a_runtime_failures.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_pilot_20260607a_runtime_failures.jsonl)
  - [qwen3_14b_turnplan_pilot_20260607a_runtime_failure_summary.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_pilot_20260607a_runtime_failure_summary.json)
- 轮次索引：
  - [artifacts/report_index.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/artifacts/report_index.md)

## 远端产物路径

按当前 AutoDL 工作区约定，本轮训练与导出产物应位于：

- work root：`/root/autodl-tmp/ecs-llm`
- adapter：`/root/autodl-tmp/ecs-llm/artifacts/adapters/qwen3-14b-turnplan-pilot-20260607a/`
- merged candidate：`/root/autodl-tmp/ecs-llm/artifacts/merged/qwen3-14b-turnplan-pilot-20260607a/`

说明：

- 本地仓库当前只镜像了 runtime 失败报告
- adapter / merged 的完整真相仍以训练端 artifact 记录为准

## 本地归档关联

- 结果摘要：[01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/01_outputs.md)
- 问题分析：[02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/02_problem_analysis.md)
- 决策收口：[03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/03_decision_log.md)
- 下一轮计划：[04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/04_next_round_plan.md)
