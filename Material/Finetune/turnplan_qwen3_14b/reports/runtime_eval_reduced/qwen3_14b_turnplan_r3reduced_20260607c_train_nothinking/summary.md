# TurnPlan Runtime Eval - qwen3_14b_turnplan_r3reduced_20260607c_train_nothinking

- total: 327
- all_null_clarify_fallback_count: 35
- effective_failure_records: 76
- top_level_track_accuracy: 0.7676
- directive_accuracy: 1.0000
- all_null_accuracy: 0.5625
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.7101
- flow_selection_accuracy: 0.9211
- slot_fill_exact_match: 0.2289
- knowledge_false_positive_rate: 0.0580
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.8410
- adjusted_protocol_gate_pass_rate: 0.9480

## High-Loss Read-Only

- count: 0
- system_success_rate: 0.0000
- list_query_success_rate: 0.0000
- work_order_runtime_success_rate: 0.0000
- service_item_detail_success_rate: 0.0000

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 73 | 0.7671 | 1.0000 | 0.9315 | 0.9315 |
| ambiguous_all_null | 80 | 0.5625 | 1.0000 | 0.4750 | 0.9125 |
| directive_exit_runtime | 40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 74 | 0.7027 | 1.0000 | 0.9595 | 0.9595 |
| work_order_business_complaint | 30 | 0.9333 | 1.0000 | 0.9333 | 0.9333 |
| work_order_business_urge | 30 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

### tp_ambiguous_all_null_train_006 (ambiguous_all_null)
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

### tp_ambiguous_all_null_train_010 (ambiguous_all_null)
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

### tp_ambiguous_all_null_train_016 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_train_017 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_train_019 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_021 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_train_029 (ambiguous_all_null)
- gold_track: all_null
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_030 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_032 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_033 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False
