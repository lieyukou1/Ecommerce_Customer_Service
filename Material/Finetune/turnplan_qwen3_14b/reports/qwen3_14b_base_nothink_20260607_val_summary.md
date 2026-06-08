# TurnPlan Runtime Eval - qwen3_14b_base_nothink_20260607_val

- total: 80
- all_null_clarify_fallback_count: 0
- effective_failure_records: 18
- top_level_track_accuracy: 0.7750
- directive_accuracy: 1.0000
- all_null_accuracy: 0.0000
- knowledge_intent_accuracy: 1.0000
- task_command_family_accuracy: 0.6047
- flow_selection_accuracy: 0.5161
- slot_fill_exact_match: 0.2353
- knowledge_false_positive_rate: 0.2093
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.9750
- adjusted_protocol_gate_pass_rate: 0.9750

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ambiguous_all_null | 6 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |
| chitchat | 8 | 0.8750 | 1.0000 | 1.0000 | 1.0000 |
| directive_exit_runtime | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| object_context_followup | 7 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| service_item_knowledge | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 7 | 0.7143 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_complaint | 5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_urge | 5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_read_only_task | 16 | 0.4375 | 1.0000 | 0.8750 | 0.8750 |

## Sample Failures

### tp_chitchat_val_002 (chitchat)
- gold_track: chitchat
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_val_000 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_val_001 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_val_002 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_val_003 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_val_004 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_val_005 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
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
