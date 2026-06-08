# round_03 Outputs

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/00_run_manifest.md)
- 报告索引: [artifacts/report_index.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/artifacts/report_index.md)

## 运行类型

- 本轮先做了 `redefinition baseline replay`
- 然后在 `reduced_round03_curated_v1` 上试跑了一轮真正的 reduced SFT
- 最后补跑了一轮 **no-thinking serving** 对照，用来剥离 Qwen3 reasoning 对 TurnPlan 评测的污染

## phase_a: 重定义 baseline 结果

### 高损失 read-only 业务结果

- 验证集 `high_loss_read_only_metrics.system_success_rate = 1.0000`
- 训练集 `high_loss_read_only_metrics.system_success_rate = 0.9437`

结论:

- 高损失 `read-only` 这条 runtime 吸收线成立
- 这部分已经不再是 reduced SFT 的主学习负担

## phase_b: reduced SFT 结果

### 训练产物

- adapter:
  - `/root/autodl-tmp/ecs-llm/artifacts/adapters/qwen3-14b-turnplan-r3reduced-20260607c`
- merged candidate:
  - `/root/autodl-tmp/ecs-llm/artifacts/merged/qwen3-14b-turnplan-r3reduced-20260607c`
- 训练摘要:
  - `train_loss = 0.1552`
  - `eval_loss = 0.0546`
  - `train_examples = 327`
  - `total_optimization_steps = 42`

### 先发现的服务侧问题

默认 Qwen3 服务方式下:

- base 与 candidate 都会出现非零比例的空 `content`
- candidate 的空 `content` 更明显，直接拉低 `json_valid_rate`
- 因此“是否关闭 thinking”必须被视为 **评测前置条件**，不是可选优化项

### 同口径主对比: `no-thinking` 验证集

| 对比对象 | top_level_track_accuracy | all_null_accuracy | task_command_family_accuracy | flow_selection_accuracy | slot_fill_exact_match | json_valid_rate | adjusted_protocol_gate_pass_rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base `Qwen3-14B` | 0.7262 | 0.2000 | 0.7222 | 0.8621 | 0.2093 | 1.0000 | 0.9881 |
| reduced SFT candidate | 0.8214 | 0.8500 | 0.6667 | 0.8276 | 0.1860 | 1.0000 | 0.9524 |

结论:

- candidate **终于在主轨道识别上压过了 base**
- 最大增益来自 `ambiguous_all_null`
- 但 `task_command_family_accuracy / flow_selection_accuracy / slot_fill_exact_match / adjusted_protocol_gate_pass_rate` 仍低于 base

### 同口径 bucket 对比: `no-thinking` 验证集

| bucket | base track_acc | candidate track_acc | 观察 |
| --- | ---: | ---: | --- |
| `ambiguous_all_null` | 0.2000 | 0.8500 | 明显提升，是当前 reduced SFT 的主要收益来源 |
| `directive_exit_runtime` | 1.0000 | 1.0000 | 稳定持平 |
| `task_interrupt_resume_cancel` | 0.7500 | 0.7000 | 略回退 |
| `active_task_slot_fill` | 0.9000 | 0.7500 | 明显回退 |
| `work_order_business_complaint` | 1.0000 | 0.8750 | 略回退 |
| `work_order_business_urge` | 1.0000 | 1.0000 | 持平 |

### candidate `no-thinking` 训练集结果

- `top_level_track_accuracy = 0.7676`
- `all_null_accuracy = 0.5625`
- `task_command_family_accuracy = 0.7101`
- `flow_selection_accuracy = 0.9211`
- `slot_fill_exact_match = 0.2289`
- `adjusted_protocol_gate_pass_rate = 0.9480`
- `active_task_slot_fill.track_accuracy = 0.7671`

这说明:

- `active_task_slot_fill` 的退化不只是验证集偶然波动
- 它在训练集上也没有学稳

## 当前阶段结论

- runtime 吸收高损失 `read-only` 这件事已经做成
- reduced SFT 在 `ambiguous_all_null` 上确实产生了真实增益
- 但 candidate 仍没有在“剩余主任务整体质量”上形成可上线的净胜
- 当前最像真问题的不是 schema，而是 **目标桶之间的学习拉扯**
- 评测必须默认使用 **no-thinking serving**

## 本轮新增产物清单

- [runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_val/metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_val/metrics.json)
- [runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_train/metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_train/metrics.json)
- [runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_val_nothinking/metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_val_nothinking/metrics.json)
- [runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_train_nothinking/metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_turnplan_r3reduced_20260607c_train_nothinking/metrics.json)
- [runtime_eval_reduced/qwen3_14b_base_reduced_round03_val_nothinking/metrics.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/reports/runtime_eval_reduced/qwen3_14b_base_reduced_round03_val_nothinking/metrics.json)
- [reduced_round03_targeted_repair_list.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_03/artifacts/reduced_round03_targeted_repair_list.md)

## 后续派生产物

### reduced `base slice`

- [records_train.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round03_base_v1/records_train.jsonl)
- [records_val.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round03_base_v1/records_val.jsonl)
- [manifest.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round03_base_v1/manifest.json)
- [summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round03_base_v1/summary.md)
- [augmentation_gaps.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round03_base_v1/augmentation_gaps.json)
- [augmentation_plan.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round03_base_v1/augmentation_plan.md)

当前 `base slice` 规模:

- train: `225`
- val: `39`
