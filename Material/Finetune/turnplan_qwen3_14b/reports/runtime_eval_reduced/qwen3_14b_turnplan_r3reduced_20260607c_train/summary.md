# TurnPlan Runtime Eval - qwen3_14b_turnplan_r3reduced_20260607c_train

- total: 327
- all_null_clarify_fallback_count: 36
- effective_failure_records: 108
- top_level_track_accuracy: 0.7248
- directive_accuracy: 0.7750
- all_null_accuracy: 0.5125
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.7585
- flow_selection_accuracy: 0.8684
- slot_fill_exact_match: 0.2530
- knowledge_false_positive_rate: 0.0386
- json_valid_rate: 0.8838
- protocol_gate_pass_rate: 0.7890
- adjusted_protocol_gate_pass_rate: 0.8991

## High-Loss Read-Only

- count: 0
- system_success_rate: 0.0000
- list_query_success_rate: 0.0000
- work_order_runtime_success_rate: 0.0000
- service_item_detail_success_rate: 0.0000

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 73 | 0.8356 | 0.9589 | 0.9315 | 0.9315 |
| ambiguous_all_null | 80 | 0.5125 | 0.7875 | 0.4500 | 0.9000 |
| directive_exit_runtime | 40 | 0.7750 | 0.7750 | 0.7750 | 0.7750 |
| task_interrupt_resume_cancel | 74 | 0.7027 | 0.9459 | 0.9324 | 0.9324 |
| work_order_business_complaint | 30 | 0.8333 | 0.9333 | 0.9000 | 0.9000 |
| work_order_business_urge | 30 | 0.9000 | 0.9000 | 0.9000 | 0.9000 |

## Sample Failures

### tp_directive_exit_runtime_train_008 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_directive_exit_runtime_train_010 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_directive_exit_runtime_train_014 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_directive_exit_runtime_train_020 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_directive_exit_runtime_train_022 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_directive_exit_runtime_train_028 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_directive_exit_runtime_train_032 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_directive_exit_runtime_train_034 (directive_exit_runtime)
- gold_track: directive
- pred_track: all_null
- json_valid: False
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `no valid json object found`

### tp_ambiguous_all_null_train_000 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_002 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_003 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_006 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True
