# round_06 Run Manifest

- round_id: `round_06`
- round_type: `contrastive_reduced_sft_validation`
- run_name: `qwen3-14b-turnplan-r6contrast-20260608a`
- base_model: `Qwen/Qwen3-14B`
- training_method: `QLoRA 4-bit`
- dataset_version: `reduced_round06_contrastive_candidate_v1`
- dataset_export: `reduced_round06_contrastive_candidate_v1_exports_llm`
- goal: validate the corrected minimized-schema export plus explicit same-utterance contrast groups under the existing Planner JSON contract
- status: `completed but not promoted`

## Dataset

- source dataset:
  - [reduced_round06_contrastive_candidate_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round06_contrastive_candidate_v1/summary.md)
- export assets:
  - [sft_train.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round06_contrastive_candidate_v1_exports_llm/sft_train.jsonl)
  - [sft_val.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round06_contrastive_candidate_v1_exports_llm/sft_val.jsonl)
  - [dataset_info.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round06_contrastive_candidate_v1_exports_llm/dataset_info.json)
  - [export_manifest.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round06_contrastive_candidate_v1_exports_llm/export_manifest.json)

## Locked Input Changes

- export now passes every record through `sanitize_record_input`
- confirmed absent from SFT user payload:
  - `runtime_state.last_route.track`
  - answer-like `focused_object.attributes.status`
  - answer-like `focused_object.attributes.amount`
  - answer-like `focused_object.attributes.summary`
  - answer-like `focused_object.attributes.price`
  - answer-like `focused_object.attributes.service_status`
  - answer-like `focused_object.attributes.description`
- train split now includes explicit contrast groups for:
  - `community_rule knowledge` vs `active task slot fill`
  - `service_item_info knowledge` vs `active task slot fill`
  - `cancel_flow` vs `exit_runtime`
  - complaint deictic phrase with object context vs no object context

## Planned Training Profile

- learning_rate: `3e-5`
- epochs: `2`
- per_device_train_batch_size: `1`
- gradient_accumulation_steps: `16`
- cutoff_len: `3072`
- lora_r: `64`
- lora_alpha: `128`
- lora_dropout: `0.05`
- report_to: `none`

## Remote Paths

- work_root: `/root/autodl-tmp/ecs-llm`
- model_dir: `/root/autodl-tmp/ecs-llm/models/Qwen3-14B`
- repo_root: `/root/autodl-tmp/ecs-llm/repo`
- adapter_dir: `/root/autodl-tmp/ecs-llm/artifacts/adapters/qwen3-14b-turnplan-r6contrast-20260608a`
- merged_dir: `/root/autodl-tmp/ecs-llm/artifacts/merged/qwen3-14b-turnplan-r6contrast-20260608a`
- train_log: `/root/autodl-tmp/ecs-llm/logs/train/qwen3-14b-turnplan-r6contrast-20260608a.log`
- merge_log: `/root/autodl-tmp/ecs-llm/logs/train/qwen3-14b-turnplan-r6merge-20260608a.log`
- candidate_eval_dir:
  - `/root/autodl-tmp/ecs-llm/repo/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r6contrast_20260608a_val_nothinking`

## Local Links

- outputs: [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/01_outputs.md)
- problem_analysis: [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/02_problem_analysis.md)
- decision_log: [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/03_decision_log.md)
- next_round_plan: [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_06/04_next_round_plan.md)
