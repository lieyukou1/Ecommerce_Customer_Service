# TurnPlan Runtime Eval - qwen3_14b_base_nothink_round03_redef_20260607a_train

- total: 450
- all_null_clarify_fallback_count: 6
- effective_failure_records: 100
- top_level_track_accuracy: 0.7778
- directive_accuracy: 1.0000
- all_null_accuracy: 0.2000
- knowledge_intent_accuracy: 0.9700
- task_command_family_accuracy: 0.6208
- flow_selection_accuracy: 0.6872
- slot_fill_exact_match: 0.2299
- knowledge_false_positive_rate: 0.2083
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.9556
- adjusted_protocol_gate_pass_rate: 0.9689

## High-Loss Read-Only

- count: 71
- system_success_rate: 0.9437
- list_query_success_rate: 0.9643
- work_order_runtime_success_rate: 1.0000
- service_item_detail_success_rate: 0.7857

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 50 | 0.8000 | 1.0000 | 1.0000 | 1.0000 |
| ambiguous_all_null | 35 | 0.2000 | 1.0000 | 0.4857 | 0.6571 |
| chitchat | 40 | 0.8750 | 1.0000 | 0.9750 | 0.9750 |
| directive_exit_runtime | 35 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| object_context_followup | 45 | 0.9556 | 1.0000 | 1.0000 | 1.0000 |
| service_item_knowledge | 55 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 45 | 0.7333 | 1.0000 | 0.9778 | 0.9778 |
| work_order_business_complaint | 30 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_urge | 30 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_read_only_task | 85 | 0.4941 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

### tp_chitchat_train_017 (chitchat)
- gold_track: chitchat
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_chitchat_train_022 (chitchat)
- gold_track: chitchat
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_chitchat_train_034 (chitchat)
- gold_track: chitchat
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_chitchat_train_035 (chitchat)
- gold_track: chitchat
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_chitchat_train_038 (chitchat)
- gold_track: chitchat
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_train_000 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_train_001 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_003 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_005 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_train_006 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_007 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_train_008 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True
