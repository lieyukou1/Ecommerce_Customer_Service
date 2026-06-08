# TurnPlan Runtime Eval - qwen3_14b_base_reduced_round03_train

- total: 327
- all_null_clarify_fallback_count: 17
- effective_failure_records: 93
- top_level_track_accuracy: 0.7187
- directive_accuracy: 1.0000
- all_null_accuracy: 0.2500
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.8068
- flow_selection_accuracy: 0.9474
- slot_fill_exact_match: 0.2349
- knowledge_false_positive_rate: 0.0531
- json_valid_rate: 0.9969
- protocol_gate_pass_rate: 0.9266
- adjusted_protocol_gate_pass_rate: 0.9786

## High-Loss Read-Only

- count: 0
- system_success_rate: 0.0000
- list_query_success_rate: 0.0000
- work_order_runtime_success_rate: 0.0000
- service_item_detail_success_rate: 0.0000

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 73 | 0.8493 | 1.0000 | 0.9863 | 0.9863 |
| ambiguous_all_null | 80 | 0.2500 | 1.0000 | 0.7250 | 0.9375 |
| directive_exit_runtime | 40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 74 | 0.7297 | 0.9865 | 0.9865 | 0.9865 |
| work_order_business_complaint | 30 | 0.9667 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_urge | 30 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

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

### tp_ambiguous_all_null_train_004 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_005 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_006 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_007 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_008 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_009 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_011 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_012 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_013 (ambiguous_all_null)
- gold_track: all_null
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True
