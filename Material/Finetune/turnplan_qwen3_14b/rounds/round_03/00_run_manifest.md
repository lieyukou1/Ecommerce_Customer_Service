# round_03 Run Manifest

- round_id: `round_03`
- run_names:
  - `qwen3_14b_base_nothink_round03_redef_20260607a`
  - `qwen3-14b-turnplan-r3reduced-20260607c`
  - `qwen3_14b_turnplan_r3reduced_20260607c_val_nothinking`
  - `qwen3_14b_turnplan_r3reduced_20260607c_train_nothinking`
  - `qwen3_14b_base_reduced_round03_val_nothinking`
- round_type: `redefinition + reduced_sft_trial`
- base_model: `Qwen/Qwen3-14B`
- training_method: `QLoRA 4-bit`
- serving_framework: `vLLM`
- dataset_versions:
  - `turnplan-phase1 / canonical_llm`
  - `turnplan-phase1 / reduced_round03_curated_v1`
- round_goal: 先验证新的任务定义与 Normalizer 吸收逻辑，再在 reduced 数据集上试跑一轮更窄的 TurnPlan SFT，判断这条线是否终于对基座产生正向增益
- run_status: `completed but not promoted`

## phase_a: 前置重定义 baseline replay

- 任务定义:
  - 暂停直接开启统一 TurnPlan SFT 的 `round_03`
  - 将高损失 `read-only` 边界改为 runtime 优先吸收
  - 统一主任务收缩到办理类意图、槽位抽取、多轮状态管理、中断/恢复/取消/退出、clarify 触发
- runtime:
  - [turn_plan_normalizer.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/turn_plan_normalizer.py) 新增高损失 `read-only` 吸收逻辑
- 评测:
  - [eval_turnplan_runtime.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/eval_turnplan_runtime.py) 新增 `high_loss_read_only_metrics`
  - 主结论不再只由 `top_level_track_accuracy` 主导

## phase_b: reduced SFT trial

- 数据:
  - [reduced_round03_curated_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round03_curated_v1/summary.md)
  - 规模: `train=327`, `val=84`
  - schema: **不变**
- 训练:
  - 框架: `LLaMA-Factory`
  - 方式: `QLoRA`
  - 学习率: `3e-5`
  - epoch: `2`
  - `batch_size=1`, `grad_accum=16`
- 部署评测:
  - merged 候选先按默认 Qwen3 服务方式回放一次
  - 中途发现 Qwen3 reasoning / 空 `content` 会污染 TurnPlan 评测
  - 随后统一改为 `default-chat-template-kwargs={"enable_thinking": false}` 再重跑关键对比

## 本轮不做的事

- 不修改 schema
- 不修改主 prompt 去硬背 `task vs knowledge` 负向规则
- 不先补一轮大规模数据再说
- 不把“默认带 reasoning 的服务结果”直接拿来做训练结论
- 不因为 `ambiguous_all_null` 提升就直接晋级候选

## 远端产物路径

- work root: `/root/autodl-tmp/ecs-llm`
- adapter:
  - `/root/autodl-tmp/ecs-llm/artifacts/adapters/qwen3-14b-turnplan-r3reduced-20260607c`
- merged:
  - `/root/autodl-tmp/ecs-llm/artifacts/merged/qwen3-14b-turnplan-r3reduced-20260607c`
- serve logs:
  - `/root/autodl-tmp/ecs-llm/logs/serve/qwen3-14b-turnplan-r3reduced-20260607c.log`
  - `/root/autodl-tmp/ecs-llm/logs/serve/Qwen3-14B-base.log`
- runtime outputs:
  - `/root/autodl-tmp/ecs-llm/repo/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_val/`
  - `/root/autodl-tmp/ecs-llm/repo/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_train/`
  - `/root/autodl-tmp/ecs-llm/repo/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_val_nothinking/`
  - `/root/autodl-tmp/ecs-llm/repo/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_train_nothinking/`
  - `/root/autodl-tmp/ecs-llm/repo/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_base_reduced_round03_val_nothinking/`

## 本地归档关联

- 结果摘要: [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/01_outputs.md)
- 问题分析: [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/02_problem_analysis.md)
- 决策收口: [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/03_decision_log.md)
- 下一轮计划: [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/04_next_round_plan.md)
- 报告索引: [artifacts/report_index.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/artifacts/report_index.md)
