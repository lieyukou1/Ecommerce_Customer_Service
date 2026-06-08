# TurnPlan Runtime Eval - qwen3_14b_turnplan_r5reduced_20260607a_val_nothinking

- total: 39
- all_null_clarify_fallback_count: 2
- effective_failure_records: 9
- top_level_track_accuracy: 0.7692
- directive_accuracy: 1.0000
- all_null_accuracy: 0.5000
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.7407
- flow_selection_accuracy: 0.8667
- slot_fill_exact_match: 0.2174
- knowledge_false_positive_rate: 0.0370
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.8205
- adjusted_protocol_gate_pass_rate: 0.8718

## High-Loss Read-Only

- count: 0
- system_success_rate: 0.0000
- list_query_success_rate: 0.0000
- work_order_runtime_success_rate: 0.0000
- service_item_detail_success_rate: 0.0000

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 10 | 0.8000 | 1.0000 | 0.9000 | 0.9000 |
| ambiguous_all_null | 6 | 0.5000 | 1.0000 | 0.1667 | 0.5000 |
| directive_exit_runtime | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 7 | 0.5714 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_complaint | 5 | 0.8000 | 1.0000 | 0.8000 | 0.8000 |
| work_order_business_urge | 5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

### tp_work_order_business_complaint_val_004 (work_order_business_complaint)
- gold_track: task
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

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

### tp_active_task_slot_fill_val_006 (active_task_slot_fill)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_active_task_slot_fill_val_007 (active_task_slot_fill)
- gold_track: task
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_val_000 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_val_003 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_ambiguous_all_null_val_005 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False
