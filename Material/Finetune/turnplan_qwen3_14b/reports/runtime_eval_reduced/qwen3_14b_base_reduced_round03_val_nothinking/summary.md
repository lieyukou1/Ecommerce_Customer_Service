# TurnPlan Runtime Eval - qwen3_14b_base_reduced_round03_val_nothinking

- total: 84
- all_null_clarify_fallback_count: 4
- effective_failure_records: 23
- top_level_track_accuracy: 0.7262
- directive_accuracy: 1.0000
- all_null_accuracy: 0.2000
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.7222
- flow_selection_accuracy: 0.8621
- slot_fill_exact_match: 0.2093
- knowledge_false_positive_rate: 0.0370
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.9405
- adjusted_protocol_gate_pass_rate: 0.9881

## High-Loss Read-Only

- count: 0
- system_success_rate: 0.0000
- list_query_success_rate: 0.0000
- work_order_runtime_success_rate: 0.0000
- service_item_detail_success_rate: 0.0000

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 20 | 0.9000 | 1.0000 | 1.0000 | 1.0000 |
| ambiguous_all_null | 20 | 0.2000 | 1.0000 | 0.7500 | 0.9500 |
| directive_exit_runtime | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 20 | 0.7500 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_complaint | 8 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_urge | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

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

### tp_task_interrupt_resume_cancel_val_001 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_task_interrupt_resume_cancel_val_005 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_ambiguous_all_null_val_006 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_ambiguous_all_null_val_008 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_ambiguous_all_null_val_009 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_ambiguous_all_null_val_011 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True
