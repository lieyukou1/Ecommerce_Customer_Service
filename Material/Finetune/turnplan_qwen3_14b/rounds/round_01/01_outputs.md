# round_01 Outputs

- 轮次入口：[00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/00_run_manifest.md)
- 原始报告索引：[artifacts/report_index.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_01/artifacts/report_index.md)

## 训练结果

- `train_loss = 0.1223`
- `eval_loss = 0.0206`
- 已产出：
  - `adapter`
  - `merged candidate`
  - runtime failure 导出

## baseline 对比

| 对比对象 | top_level_track_accuracy | directive_accuracy | all_null_accuracy | knowledge_intent_accuracy | task_command_family_accuracy | flow_selection_accuracy | slot_fill_exact_match | json_valid_rate | protocol_gate_pass_rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 远程现网 baseline | 0.8500 | - | - | - | 0.7442 | 0.6774 | 0.3529 | - | 0.9375 |
| 本地未训 Qwen3-14B | 0.7250 | - | - | - | 0.6744 | - | - | - | - |
| 本地未训 Qwen3-14B no-think | 0.7625 | - | - | - | 0.6279 | - | - | - | 0.9750 |
| round_01 pilot candidate | 0.7750 | 1.0000 | 1.0000 | 1.0000 | 0.5349 | 0.5161 | 0.2941 | 1.0000 | 0.8375 |

## runtime 回放主结果

- 验证样本总数：`80`
- failure records：`23`
- failure rate：`28.75%`
- failure type 统计：
  - `track_mismatch = 18`
  - `protocol_gate_reject = 13`
  - `json_invalid = 0`

## runtime 失败 bucket 分布

| bucket | failure_count |
| --- | ---: |
| work_order_read_only_task | 11 |
| ambiguous_all_null | 5 |
| active_task_slot_fill | 3 |
| task_interrupt_resume_cancel | 3 |
| work_order_business_complaint | 1 |

## smoke 结果

- 当前仓库已具备 smoke case 与脚本：
  - [smoke/smoke_cases.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/smoke/smoke_cases.json)
  - [scripts/run_track_smoke.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/run_track_smoke.py)
- 本轮归档范围内未追加新的 smoke 报告文件
- 其他轨道的风险验收口径以 [15_统一模型替换后的其他轨道SmokePrompts.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/15_统一模型替换后的其他轨道SmokePrompts.md) 为准

## 本轮新增产物清单

- [qwen3_14b_turnplan_pilot_20260607a_runtime_failures.csv](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_pilot_20260607a_runtime_failures.csv)
- [qwen3_14b_turnplan_pilot_20260607a_runtime_failures.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_pilot_20260607a_runtime_failures.jsonl)
- [qwen3_14b_turnplan_pilot_20260607a_runtime_failure_summary.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_pilot_20260607a_runtime_failure_summary.json)
