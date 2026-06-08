# round_06 Outputs

## Dataset + Export

- dataset: `reduced_round06_contrastive_candidate_v1`
- total_records: `288`
- train: `249`
- val: `39`
- added_contrastive_train_records: `24`
- val_set: unchanged from `reduced_round04_candidate_v1`
- export sanitation check:
  - leaked `last_route.track`: `0`
  - leaked answer-like focused object fields: `0`

## Training

- run_name: `qwen3-14b-turnplan-r6contrast-20260608a`
- status: `completed`
- train_runtime: `371.3s`
- train_loss: `0.1845`
- eval_loss: `0.0598`
- adapter:
  - `/root/autodl-tmp/ecs-llm/artifacts/adapters/qwen3-14b-turnplan-r6contrast-20260608a`
- merged candidate:
  - `/root/autodl-tmp/ecs-llm/artifacts/merged/qwen3-14b-turnplan-r6contrast-20260608a`
- logs:
  - [qwen3_14b_turnplan_r6contrast_20260608a_train.log](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_r6contrast_20260608a_train.log)
  - [qwen3_14b_turnplan_r6contrast_20260608a_merge.log](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_r6contrast_20260608a_merge.log)
  - [qwen3_14b_turnplan_r6contrast_20260608a_manifest.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/qwen3_14b_turnplan_r6contrast_20260608a_manifest.json)

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

- label: `qwen3_14b_turnplan_r6contrast_20260608a_val_nothinking`
- top_level_track_accuracy: `0.7692`
- task_command_family_accuracy: `0.7407`
- flow_selection_accuracy: `0.8000`
- slot_fill_exact_match: `0.2174`
- adjusted_protocol_gate_pass_rate: `0.8462`
- report:
  - [metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r6contrast_20260608a_val_nothinking/metrics.json)
  - [summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r6contrast_20260608a_val_nothinking/summary.md)
  - [predictions.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r6contrast_20260608a_val_nothinking/predictions.jsonl)

## Immediate Result

- candidate still did **not** beat the untouched base model
- delta vs base:
  - `top_level_track_accuracy`: `0.8205 -> 0.7692`
  - `task_command_family_accuracy`: `0.7778 -> 0.7407`
  - `flow_selection_accuracy`: `0.9333 -> 0.8000`
  - `slot_fill_exact_match`: `0.2174 -> 0.2174`
  - `adjusted_protocol_gate_pass_rate`: `0.9231 -> 0.8462`
- no promotion to serving baseline
- this round is still valuable because it cleanly validated:
  - minimized planner schema was truly used
  - contrastive rows were truly present
  - the remaining failure is not explained by the old export bug
