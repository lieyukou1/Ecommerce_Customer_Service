# TurnPlan Runtime Eval - qwen3_14b_turnplan_round2_20260607b_train

- total: 450
- all_null_clarify_fallback_count: 17
- effective_failure_records: 106
- top_level_track_accuracy: 0.7644
- directive_accuracy: 1.0000
- all_null_accuracy: 0.6286
- knowledge_intent_accuracy: 1.0000
- task_command_family_accuracy: 0.5750
- flow_selection_accuracy: 0.6089
- slot_fill_exact_match: 0.2139
- knowledge_false_positive_rate: 0.2375
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.8822
- adjusted_protocol_gate_pass_rate: 0.9200

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 50 | 0.7400 | 1.0000 | 0.9200 | 0.9200 |
| ambiguous_all_null | 35 | 0.6286 | 1.0000 | 0.4000 | 0.8857 |
| chitchat | 40 | 0.7750 | 1.0000 | 0.8250 | 0.8250 |
| directive_exit_runtime | 35 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| object_context_followup | 45 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| service_item_knowledge | 55 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 45 | 0.7111 | 1.0000 | 0.9556 | 0.9556 |
| work_order_business_complaint | 30 | 0.9333 | 1.0000 | 0.9333 | 0.9333 |
| work_order_business_urge | 30 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_read_only_task | 85 | 0.3412 | 1.0000 | 0.8000 | 0.8000 |

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

### tp_chitchat_train_032 (chitchat)
- gold_track: chitchat
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_chitchat_train_033 (chitchat)
- gold_track: chitchat
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_chitchat_train_034 (chitchat)
- gold_track: chitchat
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_chitchat_train_035 (chitchat)
- gold_track: chitchat
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_chitchat_train_036 (chitchat)
- gold_track: chitchat
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_chitchat_train_038 (chitchat)
- gold_track: chitchat
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_chitchat_train_039 (chitchat)
- gold_track: chitchat
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

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
