# round_05 Outputs

## Training

- run_name: `qwen3-14b-turnplan-r5reduced-20260607a`
- status: `completed`
- train_runtime: `359.1s`
- train_loss: `0.1941`
- eval_loss: `0.0602`
- adapter:
  - `/root/autodl-tmp/ecs-llm/artifacts/adapters/qwen3-14b-turnplan-r5reduced-20260607a`
- merged candidate:
  - `/root/autodl-tmp/ecs-llm/artifacts/merged/qwen3-14b-turnplan-r5reduced-20260607a`
- logs:
  - [qwen3_14b_turnplan_r5reduced_20260607a_train.log](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_r5reduced_20260607a_train.log)
  - [qwen3_14b_turnplan_r5reduced_20260607a_merge.log](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_r5reduced_20260607a_merge.log)

## Val Runtime Replay

### Base

- label: `qwen3_14b_base_reduced_round04_val_nothinking`
- top_level_track_accuracy: `0.8205`
- task_command_family_accuracy: `0.7778`
- flow_selection_accuracy: `0.9333`
- slot_fill_exact_match: `0.2174`
- adjusted_protocol_gate_pass_rate: `0.9231`
- report:
  - [metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_base_reduced_round04_val_nothinking/metrics.json)
  - [summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_base_reduced_round04_val_nothinking/summary.md)

### Candidate

- label: `qwen3_14b_turnplan_r5reduced_20260607a_val_nothinking`
- top_level_track_accuracy: `0.7692`
- task_command_family_accuracy: `0.7407`
- flow_selection_accuracy: `0.8667`
- slot_fill_exact_match: `0.2174`
- adjusted_protocol_gate_pass_rate: `0.8718`
- report:
  - [metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r5reduced_20260607a_val_nothinking/metrics.json)
  - [summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r5reduced_20260607a_val_nothinking/summary.md)

## Immediate Result

- candidate did **not** beat the untouched base model on the reduced round_04 val replay
- the clearest regressions are:
  - `task_command_family_accuracy`: `0.7778 -> 0.7407`
  - `flow_selection_accuracy`: `0.9333 -> 0.8667`
  - `adjusted_protocol_gate_pass_rate`: `0.9231 -> 0.8718`
- no promotion to serving baseline
