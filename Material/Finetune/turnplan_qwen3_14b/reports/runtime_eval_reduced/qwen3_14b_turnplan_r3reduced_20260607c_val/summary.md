# TurnPlan Runtime Eval - qwen3_14b_turnplan_r3reduced_20260607c_val

- total: 84
- all_null_clarify_fallback_count: 12
- effective_failure_records: 22
- top_level_track_accuracy: 0.7738
- directive_accuracy: 0.8000
- all_null_accuracy: 0.6000
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.7222
- flow_selection_accuracy: 0.7241
- slot_fill_exact_match: 0.2558
- knowledge_false_positive_rate: 0.0000
- json_valid_rate: 0.8929
- protocol_gate_pass_rate: 0.7500
- adjusted_protocol_gate_pass_rate: 0.8929

## High-Loss Read-Only

- count: 0
- system_success_rate: 0.0000
- list_query_success_rate: 0.0000
- work_order_runtime_success_rate: 0.0000
- service_item_detail_success_rate: 0.0000

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 20 | 0.9000 | 0.9000 | 0.9000 | 0.9000 |
| ambiguous_all_null | 20 | 0.6000 | 0.8500 | 0.2500 | 0.8500 |
| directive_exit_runtime | 10 | 0.8000 | 0.8000 | 0.8000 | 0.8000 |
| task_interrupt_resume_cancel | 20 | 0.7000 | 0.9500 | 0.9500 | 0.9500 |
| work_order_business_complaint | 8 | 0.8750 | 0.8750 | 0.8750 | 0.8750 |
| work_order_business_urge | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

### tp_directive_exit_runtime_val_000 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

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
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: True
- parse_error: `no valid json object found`

### tp_work_order_business_complaint_val_001 (work_order_business_complaint)
- gold_track: task
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_task_interrupt_resume_cancel_val_001 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_task_interrupt_resume_cancel_val_004 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_task_interrupt_resume_cancel_val_005 (task_interrupt_resume_cancel)
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
