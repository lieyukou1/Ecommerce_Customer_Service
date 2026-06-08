# round_04 Run Manifest

- round_id: `round_04`
- round_type: `protocol_compatibility_refactor`
- base_model_scope: `Qwen/Qwen3-14B TurnPlan pipeline`
- status: `completed`
- goal: 在不改 `TurnPlan JSON` 最终合同的前提下，完成 Planner 协议兼容重构，并把数据审计升级为跨字段联合审计

## 本轮改动范围

- backend:
  - [turn_plan_normalizer.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/turn_plan_normalizer.py)
  - [read_only_resolver.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/read_only_resolver.py)
- dataset scripts:
  - [input_sanitizer.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/input_sanitizer.py)
  - [audit_rules.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/audit_rules.py)
  - [audit_helpers.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/audit_helpers.py)
  - [metrics.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/metrics.py)
  - [validate_dataset.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/validate_dataset.py)
  - [audit_dataset.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/audit_dataset.py)
  - [export_sft.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/export_sft.py)
- schema:
  - [canonical-record.schema.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/schema/canonical-record.schema.json)
  - [dataset_contract.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/dataset_contract.py)

## 本轮不改的东西

- 不改最终 `TurnPlan JSON` 输出 shape
- 不新增第二次 Planner LLM 调用
- 不直接开始新一轮 reduced SFT
- 不在这轮顺手改执行层协议

## 本轮运行与验证

- `python -m py_compile ...`：通过
- [validate_dataset.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/validate_dataset.py)：通过
- [audit_dataset.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/audit_dataset.py)：通过
- [export_sft.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/export_sft.py)：通过
- `TurnPlanNormalizer` 最小运行验证：通过，`knowledge(work_order_info)` 可被兼容改写为只读 `task flow`

## 关联稳定文档

- [21_Planner协议兼容重构与联合审计规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/21_Planner协议兼容重构与联合审计规范.md)

## 关联产物

- [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/01_outputs.md)
- [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/02_problem_analysis.md)
- [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/03_decision_log.md)
- [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/04_next_round_plan.md)
- [artifacts/report_index.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/artifacts/report_index.md)
