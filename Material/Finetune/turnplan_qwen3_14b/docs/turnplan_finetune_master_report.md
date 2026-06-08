# TurnPlan 微调总报告

- 最后更新时间: `2026-06-07`
- 文档定位: TurnPlan 微调项目的跨轮高密度入口
- 上级入口: [README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/README.md)

## 当前阶段结论

- 当前训练主线: `Qwen3-14B + QLoRA + vLLM + LLaMA-Factory`
- 当前微调目标: 只微调 `TurnPlan`
- 当前稳定蓝版本: 远程现网 baseline 继续保留
- 当前轮次状态:
  - `round_01`: 已完成，未晋级
  - `round_02`: 已完成，未晋级
  - `round_03`: 已完成“重定义 + reduced 试跑”验证，未晋级
  - `round_04`: 已完成“协议兼容重构 + 联合审计升级 + reduced candidate 重建”，等待下一轮 reduced SFT 验证

## 稳定入口

0. [22_TurnPlan微调全链路复盘报告.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/22_TurnPlan微调全链路复盘报告.md)
0. [23_TurnPlan微调证据与轮次附录.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/23_TurnPlan微调证据与轮次附录.md)
1. [11_TurnPlan微调实施方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md)
2. [12_通用微调项目全流程指南.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/12_通用微调项目全流程指南.md)
3. [13_AutoDL4090训练目录与落盘规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/13_AutoDL4090训练目录与落盘规范.md)
4. [14_TurnPlan训练前Baseline执行清单.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/14_TurnPlan训练前Baseline执行清单.md)
5. [15_统一模型替换后的其他轨道SmokePrompts.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/15_统一模型替换后的其他轨道SmokePrompts.md)
6. [16_连续两轮未压过基座时的诊断规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/16_连续两轮未压过基座时的诊断规范.md)
7. [17_Round03前置重定义方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/17_Round03前置重定义方案.md)
8. [18_高损失ReadOnly与Round03评测口径.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/18_高损失ReadOnly与Round03评测口径.md)
9. [19_ReducedRound03训练方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/19_ReducedRound03训练方案.md)
10. [20_ReducedRound03数据切分与扩样规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/20_ReducedRound03数据切分与扩样规范.md)
11. [21_Planner协议兼容重构与联合审计规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/21_Planner协议兼容重构与联合审计规范.md)

## 轮次摘要

### round_01

- 入口:
  - [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/00_run_manifest.md)
  - [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/01_outputs.md)
  - [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/02_problem_analysis.md)
  - [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/03_decision_log.md)
  - [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/04_next_round_plan.md)
- 结果: 首轮统一 SFT 未压过未训练基座，主错法集中在 `task -> knowledge` 与 `task -> all_null`

### round_02

- 入口:
  - [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/00_run_manifest.md)
  - [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/01_outputs.md)
  - [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/02_problem_analysis.md)
  - [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/03_decision_log.md)
  - [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/04_next_round_plan.md)
- 结果: 降学习率和小补样本后仍未晋级，问题被确认更像任务定义与监督空间不匹配

### round_03

- 入口:
  - [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/00_run_manifest.md)
  - [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/01_outputs.md)
  - [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/02_problem_analysis.md)
  - [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/03_decision_log.md)
  - [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/04_next_round_plan.md)
- 结果: 验证了“高损失 read-only 先由 runtime 吸收”这条路是成立的，但 reduced SFT 仍未正式验证完

### round_04

- 入口:
  - [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/00_run_manifest.md)
  - [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/01_outputs.md)
  - [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/02_problem_analysis.md)
  - [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/03_decision_log.md)
  - [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/04_next_round_plan.md)
  - [reduced_round04_context_map.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/artifacts/reduced_round04_context_map.md)
- 本轮目标: 不开新训练，先完成协议兼容重构、联合审计升级、reduced 数据重切与重建
- 实际产出:
  - `TurnPlanNormalizer -> ReadOnlyResolver` 职责切开
  - canonical safe export 跑通
  - reduced triage 完成
  - `active_task_slot_fill` 完成 focused repair
  - `ambiguous_all_null / directive_exit_runtime` 完成整桶重建
  - `reduced_round04_candidate_v1` 已组装完成
- reduced candidate 结论:
  - total `264`
  - `sft_ready_pass_rate = 1.0`
  - `duplicate_pairs = 0`
  - `unsafe_records = 0`
- reduced candidate 定位:
  - `reduced_round04_candidate_v1 = validation-oriented training set`
  - 下一阶段目标不是直接上线，而是先验证 unified Planner SFT 在干净前提下是否存在净收益
  - 若验证成立，再继续扩成 `production-oriented expansion set`
- 当前意义:
  - 高损失 read-only 已从主训练矛盾中挪开
  - 伪上下文已被联合审计挡掉
  - 下一轮终于可以做一次更干净的 reduced SFT 验证

## 当前最重要的结论

当前最大的系统性问题已经不再是“样本够不够多”，而是：

- 统一 TurnPlan SFT 是否真能在剩余核心能力上压过 base
- 如果不能，失败到底是监督空间张力，还是某个具体机制仍然没被教稳

而 round_04 的价值在于：

- 它已经把“脏数据”这个大噪声源大幅压下去了
- 使下一轮验证终于具备解释力

## 当前最佳判断

- 蓝版本继续保留远程现网 baseline
- 训练链路本身已经跑通
- 当前最稳的下一步是：
  1. 用 `reduced_round04_candidate_v1` 跑 base baseline
  2. 跑 1 轮 reduced SFT
  3. 用 reduced 口径做一次真正的正面对比

## 下一步待验证事项

- reduced candidate 上的 unified Planner SFT 能否在主 bucket 上带来净收益
- `active_task_slot_fill` 的短句补槽是否能明显提升
- `ambiguous_all_null` 与 `directive_exit_runtime` 是否已不再被脏上下文拖累
- 若仍失败，是否说明剩余问题已主要来自监督空间与统一协议之间的残余张力

## round_06 补充

- 入口:
  - [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/00_run_manifest.md)
  - [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/01_outputs.md)
  - [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/02_problem_analysis.md)
  - [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/03_decision_log.md)
  - [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/04_next_round_plan.md)
- 本轮目标:
  - 用真正的 minimized schema export 和显式 contrast groups 再做一次 reduced SFT 验证
- 实际产出:
  - `reduced_round06_contrastive_candidate_v1`
  - `reduced_round06_contrastive_candidate_v1_exports_llm`
  - `qwen3-14b-turnplan-r6contrast-20260608a`
- 结果:
  - candidate 仍未压过 base
  - `top_level_track_accuracy`: `0.8205 -> 0.7692`
  - `task_command_family_accuracy`: `0.7778 -> 0.7407`
  - `flow_selection_accuracy`: `0.9333 -> 0.8000`
  - `adjusted_protocol_gate_pass_rate`: `0.9231 -> 0.8462`
- 这轮的意义:
  - 可以正式排除“旧 export 泄漏”是主要解释
  - 可以正式排除“只是缺 contrast rows”是主要解释
  - 剩余问题进一步收缩到监督目标与 base 语义先验之间的张力
