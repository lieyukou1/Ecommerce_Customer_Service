# TurnPlan Runtime Eval - qwen3_14b_turnplan_round2_20260607b_val

- total: 80
- all_null_clarify_fallback_count: 5
- effective_failure_records: 18
- top_level_track_accuracy: 0.7750
- directive_accuracy: 1.0000
- all_null_accuracy: 1.0000
- knowledge_intent_accuracy: 1.0000
- task_command_family_accuracy: 0.5814
- flow_selection_accuracy: 0.5161
- slot_fill_exact_match: 0.2353
- knowledge_false_positive_rate: 0.2326
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.8500
- adjusted_protocol_gate_pass_rate: 0.9125

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 10 | 0.8000 | 1.0000 | 0.9000 | 0.9000 |
| ambiguous_all_null | 6 | 1.0000 | 1.0000 | 0.1667 | 1.0000 |
| chitchat | 8 | 0.8750 | 1.0000 | 1.0000 | 1.0000 |
| directive_exit_runtime | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| object_context_followup | 7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| service_item_knowledge | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 7 | 0.5714 | 1.0000 | 0.8571 | 0.8571 |
| work_order_business_complaint | 5 | 0.8000 | 1.0000 | 0.8000 | 0.8000 |
| work_order_business_urge | 5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_read_only_task | 16 | 0.3125 | 1.0000 | 0.7500 | 0.7500 |

## Sample Failures

### tp_chitchat_val_002 (chitchat)
- gold_track: chitchat
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_work_order_read_only_task_val_000 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_work_order_read_only_task_val_001 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_work_order_read_only_task_val_002 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_work_order_read_only_task_val_004 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_work_order_read_only_task_val_005 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_work_order_read_only_task_val_006 (work_order_read_only_task)
- gold_track: task
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_work_order_read_only_task_val_008 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_work_order_read_only_task_val_009 (work_order_read_only_task)
- gold_track: task
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_work_order_read_only_task_val_010 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_work_order_read_only_task_val_011 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_work_order_read_only_task_val_014 (work_order_read_only_task)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True
