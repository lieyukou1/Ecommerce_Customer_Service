# TurnPlan Runtime Eval - qwen3_14b_base_reduced_round03_val

- total: 84
- all_null_clarify_fallback_count: 8
- effective_failure_records: 24
- top_level_track_accuracy: 0.7381
- directive_accuracy: 1.0000
- all_null_accuracy: 0.4000
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.7407
- flow_selection_accuracy: 0.7931
- slot_fill_exact_match: 0.2791
- knowledge_false_positive_rate: 0.0370
- json_valid_rate: 0.9524
- protocol_gate_pass_rate: 0.8333
- adjusted_protocol_gate_pass_rate: 0.9286

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
| ambiguous_all_null | 20 | 0.4000 | 0.9000 | 0.4000 | 0.8000 |
| directive_exit_runtime | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 20 | 0.6000 | 0.9000 | 0.9000 | 0.9000 |
| work_order_business_complaint | 8 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_urge | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

### tp_ambiguous_all_null_val_000 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_val_002 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
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

### tp_task_interrupt_resume_cancel_val_006 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_ambiguous_all_null_val_007 (ambiguous_all_null)
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
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_r3_ambiguous_all_null_val_011 (ambiguous_all_null)
- gold_track: all_null
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: True
- parse_error: `no valid json object found`

### tp_r3_ambiguous_all_null_val_013 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True
