# TurnPlan Qwen3-14B Finetune Workspace

- 最后修改时间: 2026-06-07
- 文档定位: TurnPlan 微调训练、评测、归档与复盘的统一工作区
- 上级入口: [PROJECT_CONTEXT.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/PROJECT_CONTEXT.md)

## 目录结构

- `configs/`
  - 稳定配置模板、数据集映射、通用参数配置
- `scripts/`
  - 训练辅助、评测、导出、服务启动脚本
- `reports/`
  - 只存程序导出的原始结果，不混放人工分析
- `docs/`
  - 跨轮稳定文档区
- `rounds/`
  - 单轮归档区
- `smoke/`
  - 统一模型替换后的 smoke case 资产

## 当前阅读顺序

1. [docs/turnplan_finetune_master_report.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/turnplan_finetune_master_report.md)
2. [docs/11_TurnPlan微调实施方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md)
3. [docs/14_TurnPlan训练前Baseline执行清单.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/14_TurnPlan训练前Baseline执行清单.md)
4. [docs/15_统一模型替换后的其他轨道SmokePrompts.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/15_统一模型替换后的其他轨道SmokePrompts.md)
5. [docs/16_连续两轮未压过基座时的诊断规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/16_连续两轮未压过基座时的诊断规范.md)
6. [docs/17_Round03前置重定义方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/17_Round03前置重定义方案.md)
7. [docs/18_高损失ReadOnly与Round03评测口径.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/18_高损失ReadOnly与Round03评测口径.md)
8. [docs/19_ReducedRound03训练方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/19_ReducedRound03训练方案.md)
9. [docs/20_ReducedRound03数据切分与扩样规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/20_ReducedRound03数据切分与扩样规范.md)
10. [rounds/round_03/00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/00_run_manifest.md)

## 稳定文档区

- [docs/11_TurnPlan微调实施方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md)
  - 项目级 TurnPlan 微调、评测、部署、回滚方案
- [docs/12_通用微调项目全流程指南.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/12_通用微调项目全流程指南.md)
  - 从需求定义到部署灾备的通用微调手册
- [docs/13_AutoDL4090训练目录与落盘规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/13_AutoDL4090训练目录与落盘规范.md)
  - 当前 AutoDL 4090 单机环境的目录、缓存与产物落盘规范
- [docs/14_TurnPlan训练前Baseline执行清单.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/14_TurnPlan训练前Baseline执行清单.md)
  - 训练前 baseline、数据门禁与验收清单
- [docs/15_统一模型替换后的其他轨道SmokePrompts.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/15_统一模型替换后的其他轨道SmokePrompts.md)
  - `knowledge / clarify / chitchat` 的轻评测 prompts
- [docs/16_连续两轮未压过基座时的诊断规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/16_连续两轮未压过基座时的诊断规范.md)
  - 连续两轮未压过基座时的停训与诊断流程
- [docs/17_Round03前置重定义方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/17_Round03前置重定义方案.md)
  - `round_03` 开训前的任务重定义、边界重定义与推进顺序
- [docs/18_高损失ReadOnly与Round03评测口径.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/18_高损失ReadOnly与Round03评测口径.md)
  - 主训练集收缩口径与高损失 `read-only` system eval 口径
- [docs/19_ReducedRound03训练方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/19_ReducedRound03训练方案.md)
  - reduced `round_03` 的主任务收缩、风险控制与晋级门槛
- [docs/20_ReducedRound03数据切分与扩样规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/20_ReducedRound03数据切分与扩样规范.md)
  - reduced `base slice` 的切分规则、扩样优先级与验收门槛

## 单轮归档规则

每一轮固定补齐:

- `00_run_manifest.md`
- `01_outputs.md`
- `02_problem_analysis.md`
- `03_decision_log.md`
- `04_next_round_plan.md`
- `artifacts/`

这些文档必须连续回答 5 件事:

1. 这轮产出了什么
2. 暴露了什么问题
3. 问题怎么被拆解和归因
4. 最终定下了什么调整项
5. 下一轮按什么配置继续跑

## 原始结果区约束

`reports/` 只保留:

- `json`
- `jsonl`
- `csv`
- 程序导出的 `summary`

人工分析、决策和讨论统一进入 `rounds/<round_id>/` 或 `docs/`。
