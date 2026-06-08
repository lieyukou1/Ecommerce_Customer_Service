# round_05 Run Manifest

- round_id: `round_05`
- round_type: `reduced_sft_validation`
- run_name: `qwen3-14b-turnplan-r5reduced-20260607a`
- base_model: `Qwen/Qwen3-14B`
- training_method: `QLoRA 4-bit`
- dataset_version: `reduced_round04_candidate_v1`
- dataset_export: `reduced_round04_candidate_v1_exports_llm`
- goal: validate whether the protocol-compatible reduced slice can produce a measurable gain over the untouched base model
- status: `completed but not promoted`

## Dataset

- canonical source:
  - [reduced_round04_candidate_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_candidate_v1/summary.md)
- export assets:
  - [sft_train.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_candidate_v1_exports_llm/sft_train.jsonl)
  - [sft_val.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_candidate_v1_exports_llm/sft_val.jsonl)
  - [dataset_info.json](/D:/Desktop/SGG_Project\Ecommerce_Customer_Service\Material\Datasets\turnplan-phase1\reduced_round04_candidate_v1_exports_llm\dataset_info.json)

## Planned Training Profile

- learning_rate: `3e-5`
- epochs: `2`
- per_device_train_batch_size: `1`
- gradient_accumulation_steps: `16`
- cutoff_len: `3072`
- lora_r: `64`
- lora_alpha: `128`
- lora_dropout: `0.05`

## Remote Paths

- work_root: `/root/autodl-tmp/ecs-llm`
- model_dir: `/root/autodl-tmp/ecs-llm/models/Qwen3-14B`
- repo_root: `/root/autodl-tmp/ecs-llm/repo`
- adapter_dir: `/root/autodl-tmp/ecs-llm/artifacts/adapters/qwen3-14b-turnplan-r5reduced-20260607a`
- merged_dir: `/root/autodl-tmp/ecs-llm/artifacts/merged/qwen3-14b-turnplan-r5reduced-20260607a`
- train_log: `/root/autodl-tmp/ecs-llm/logs/train/qwen3-14b-turnplan-r5reduced-20260607a.log`
- merge_log: `/root/autodl-tmp/ecs-llm/logs/train/qwen3-14b-turnplan-r5merge-20260607a.log`

## Local Links

- outputs: [01_outputs.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_05/01_outputs.md)
- problem_analysis: [02_problem_analysis.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_05/02_problem_analysis.md)
- decision_log: [03_decision_log.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_05/03_decision_log.md)
- next_round_plan: [04_next_round_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_05/04_next_round_plan.md)
