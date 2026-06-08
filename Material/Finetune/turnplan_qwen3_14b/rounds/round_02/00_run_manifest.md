# round_02 Run Manifest

- round_id: `round_02`
- run_name: `qwen3-14b-turnplan-round2-20260607b`
- round_type: `targeted_followup`
- base_model: `Qwen/Qwen3-14B`
- training_method: `QLoRA 4-bit`
- training_framework: `LLaMA-Factory`
- serving_framework: `vLLM`
- dataset_version: `turnplan-phase1 / exports_llm`
- round_goal: 在不做大规模数据重写的前提下，验证 round 1 的小范围修正是否能把 TurnPlan 主要错法往正确方向拉。

## 本轮改动范围

- 评测口径:
  - 新增 `all_null_as_expected_clarify_fallback`
  - `effective_gate_pass` 进入主统计
  - 新增 `adjusted_protocol_gate_pass_rate`
  - 新增 `knowledge_false_positive_rate`
- 数据:
  - 只做 7 条定向修订
  - 重点覆盖 `work_order_read_only_task`
  - 小补 `active_task_slot_fill`
  - 小补 `cancel_flow vs exit_runtime`
- 训练脚本:
  - `render_llamafactory_recipe.py` 支持 `--report-to`
  - 本轮使用 `report_to=none`，绕开 W&B 登录阻塞

## 训练配置摘要

- quantization: `NF4 4-bit`
- compute dtype: `bf16`
- LoRA:
  - `rank=64`
  - `alpha=128`
  - `dropout=0.05`
- cutoff_len: `3072`
- per-device batch size: `1`
- gradient accumulation: `16`
- learning rate: `5e-5`
- epochs: `1`
- save/eval steps: `10`
- logging steps: `5`

## 远端产物路径

- work root: `/root/autodl-tmp/ecs-llm`
- adapter: `/root/autodl-tmp/ecs-llm/artifacts/adapters/qwen3-14b-turnplan-round2-20260607b/`
- merged candidate: `/root/autodl-tmp/ecs-llm/artifacts/merged/qwen3-14b-turnplan-round2-20260607b/`
- train log: `/root/autodl-tmp/ecs-llm/logs/train/qwen3-14b-turnplan-round2-20260607b.log`

## 本地归档关联

- 结果摘要: [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/01_outputs.md)
- 问题分析: [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/02_problem_analysis.md)
- 决策收口: [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/03_decision_log.md)
- 下轮计划: [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/04_next_round_plan.md)
- 报告索引: [artifacts/report_index.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/artifacts/report_index.md)
