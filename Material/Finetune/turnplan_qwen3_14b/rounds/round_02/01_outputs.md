# round_02 Outputs

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/00_run_manifest.md)
- 报告索引: [artifacts/report_index.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_02/artifacts/report_index.md)

## 训练结果

- `train_loss = 0.1533`
- `eval_loss = 0.0337`
- `train_runtime = 338.84s`
- `eval_runtime = 18.00s`
- 已产出:
  - `adapter`
  - `merged candidate`
  - runtime eval 全量预测
  - smoke 结果

## baseline 对比

| 对比对象 | top_level_track_accuracy | task_command_family_accuracy | flow_selection_accuracy | slot_fill_exact_match | protocol_gate_pass_rate | adjusted_protocol_gate_pass_rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 本地未训 Qwen3-14B no-think | 0.7750 | 0.6047 | 0.5161 | 0.2353 | 0.9750 | 0.9750 |
| 远程现网 baseline | 0.8500 | 0.7442 | 0.6774 | 0.3529 | 0.9375 | - |
| round_01 pilot candidate | 0.7750 | 0.5349 | 0.5161 | 0.2941 | 0.8375 | - |
| round_02 candidate | 0.7750 | 0.5814 | 0.5161 | 0.2353 | 0.8500 | 0.9125 |

## train split 对照结果

| 对比对象 | top_level_track_accuracy | task_command_family_accuracy | flow_selection_accuracy | slot_fill_exact_match | protocol_gate_pass_rate | adjusted_protocol_gate_pass_rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 本地未训 Qwen3-14B no-think | 0.7800 | 0.6250 | 0.6872 | 0.2353 | 0.9311 | 0.9444 |
| round_02 candidate | 0.7644 | 0.5750 | 0.6089 | 0.2139 | 0.8822 | 0.9200 |

## runtime 回放主结果

- 验证样本总数: `80`
- `all_null_clarify_fallback_count = 5`
- `effective_failure_records = 18`
- `json_valid_rate = 1.0000`
- `directive_accuracy = 1.0000`
- `all_null_accuracy = 1.0000`
- `knowledge_intent_accuracy = 1.0000`
- `knowledge_false_positive_rate = 0.2326`

## runtime failure bucket 分布

| bucket | effective_failure_count |
| --- | ---: |
| work_order_read_only_task | 11 |
| task_interrupt_resume_cancel | 3 |
| active_task_slot_fill | 2 |
| chitchat | 1 |
| work_order_business_complaint | 1 |

## smoke 结果

- 样本数: `15`
- `json_like = 0`
- `too_short = 0`
- `hard_tone = 0`
- `refusal_like = 0`

## 本轮新增产物清单

- [qwen3_14b_turnplan_round2_20260607b_train_results.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_train_results.json)
- [qwen3_14b_turnplan_round2_20260607b_eval_results.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_eval_results.json)
- [qwen3_14b_turnplan_round2_20260607b_all_results.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_all_results.json)
- [qwen3_14b_turnplan_round2_20260607b_train.log](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_train.log)
- [qwen3_14b_turnplan_round2_20260607b_val_metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_val_metrics.json)
- [qwen3_14b_turnplan_round2_20260607b_val_predictions.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_val_predictions.jsonl)
- [qwen3_14b_turnplan_round2_20260607b_val_summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_val_summary.md)
- [qwen3_14b_turnplan_round2_20260607b_val_failure_summary.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_val_failure_summary.json)
- [qwen3_14b_turnplan_round2_20260607b_smoke_results.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_smoke_results.json)
- [qwen3_14b_turnplan_round2_20260607b_smoke_summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_round2_20260607b_smoke_summary.md)
- [qwen3_14b_base_nothink_20260607_val_metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_base_nothink_20260607_val_metrics.json)
- [qwen3_14b_base_nothink_20260607_train_metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_base_nothink_20260607_train_metrics.json)
- [qwen3_14b_round2_systemic_diagnostic.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_round2_systemic_diagnostic.md)
