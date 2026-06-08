# Round 2 vs Base Diagnostic

## Key Judgment

- `round_02` does not outperform the untrained `Qwen3-14B no-think` baseline on the key protocol metrics.
- The gap is visible not only on `val`, but also on `train`.
- This points more toward a task-definition / label-boundary / SFT-shaping problem than a simple generalization problem.

## VAL Metric Comparison

| metric | base_nothink | round_02 | delta |
| --- | ---: | ---: | ---: |
| top_level_track_accuracy | 0.7750 | 0.7750 | +0.0000 |
| task_command_family_accuracy | 0.6047 | 0.5814 | -0.0233 |
| flow_selection_accuracy | 0.5161 | 0.5161 | +0.0000 |
| slot_fill_exact_match | 0.2353 | 0.2353 | +0.0000 |
| protocol_gate_pass_rate | 0.9750 | 0.8500 | -0.1250 |
| adjusted_protocol_gate_pass_rate | 0.9750 | 0.9125 | -0.0625 |
| knowledge_false_positive_rate | 0.2093 | 0.2326 | +0.0233 |

| bucket | base_track_acc | round_02_track_acc | delta |
| --- | ---: | ---: | ---: |
| work_order_read_only_task | 0.4375 | 0.3125 | -0.1250 |
| active_task_slot_fill | 1.0000 | 0.8000 | -0.2000 |
| task_interrupt_resume_cancel | 0.7143 | 0.5714 | -0.1429 |
| ambiguous_all_null | 0.0000 | 1.0000 | +1.0000 |

## TRAIN Metric Comparison

| metric | base_nothink | round_02 | delta |
| --- | ---: | ---: | ---: |
| top_level_track_accuracy | 0.7800 | 0.7644 | -0.0156 |
| task_command_family_accuracy | 0.6250 | 0.5750 | -0.0500 |
| flow_selection_accuracy | 0.6872 | 0.6089 | -0.0782 |
| slot_fill_exact_match | 0.2353 | 0.2139 | -0.0214 |
| protocol_gate_pass_rate | 0.9311 | 0.8822 | -0.0489 |
| adjusted_protocol_gate_pass_rate | 0.9444 | 0.9200 | -0.0244 |
| knowledge_false_positive_rate | 0.2083 | 0.2375 | +0.0292 |

| bucket | base_track_acc | round_02_track_acc | delta |
| --- | ---: | ---: | ---: |
| work_order_read_only_task | 0.4941 | 0.3412 | -0.1529 |
| active_task_slot_fill | 0.8000 | 0.7400 | -0.0600 |
| task_interrupt_resume_cancel | 0.7333 | 0.7111 | -0.0222 |
| ambiguous_all_null | 0.2000 | 0.6286 | +0.4286 |

## Outcome Overlap

| split | both_ok | base_only_ok | round2_only_ok | both_fail |
| --- | ---: | ---: | ---: | ---: |
| val | 56 | 6 | 6 | 12 |
| train | 328 | 23 | 16 | 83 |

## Base-only / Round2-only by Bucket

### VAL

| bucket | base_only_ok | round2_only_ok |
| --- | ---: | ---: |
| active_task_slot_fill | 2 | 0 |
| ambiguous_all_null | 0 | 6 |
| task_interrupt_resume_cancel | 1 | 0 |
| work_order_business_complaint | 1 | 0 |
| work_order_read_only_task | 2 | 0 |

### TRAIN

| bucket | base_only_ok | round2_only_ok |
| --- | ---: | ---: |
| active_task_slot_fill | 3 | 0 |
| ambiguous_all_null | 0 | 15 |
| chitchat | 4 | 0 |
| object_context_followup | 0 | 1 |
| task_interrupt_resume_cancel | 1 | 0 |
| work_order_business_complaint | 2 | 0 |
| work_order_read_only_task | 13 | 0 |

## Read-only Counterexamples (base right, round2 wrong)

- count: 2

### tp_work_order_read_only_task_val_006
- user_message: 主要想知道上门时间定了没有，只看这个工单就行
- history_last: assistant: 好的，咱们就围绕这个工单。
- focused_object: work_order / 玄关可视对讲无声
- gold_track: task
- base_pred: {"task": {"commands": [{"command": "start_flow", "flow": "service_progress_tracking"}]}, "knowledge": null, "chitchat": null, "directive": null}
- round2_pred: {"task": null, "knowledge": null, "chitchat": null, "directive": null}

### tp_work_order_read_only_task_val_009
- user_message: 帮我看下我名下现在有几个工单，我就想确认这个
- history_last: assistant: 可以，我先帮你看看。
- gold_track: task
- base_pred: {"task": {"commands": [{"command": "start_flow", "flow": "resident_work_orders_list_query"}]}, "knowledge": null, "chitchat": null, "directive": null}
- round2_pred: {"task": null, "knowledge": null, "chitchat": null, "directive": null}
