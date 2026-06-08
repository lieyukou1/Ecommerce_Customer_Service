# TurnPlan Runtime Eval - qwen3_14b_turnplan_r3reduced_20260607c_val_nothinking

- total: 84
- all_null_clarify_fallback_count: 15
- effective_failure_records: 15
- top_level_track_accuracy: 0.8214
- directive_accuracy: 1.0000
- all_null_accuracy: 0.8500
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.6667
- flow_selection_accuracy: 0.8276
- slot_fill_exact_match: 0.1860
- knowledge_false_positive_rate: 0.0556
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.7738
- adjusted_protocol_gate_pass_rate: 0.9524

## High-Loss Read-Only

- count: 0
- system_success_rate: 0.0000
- list_query_success_rate: 0.0000
- work_order_runtime_success_rate: 0.0000
- service_item_detail_success_rate: 0.0000

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 20 | 0.7500 | 1.0000 | 0.9000 | 0.9000 |
| ambiguous_all_null | 20 | 0.8500 | 1.0000 | 0.2500 | 1.0000 |
| directive_exit_runtime | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 20 | 0.7000 | 1.0000 | 0.9500 | 0.9500 |
| work_order_business_complaint | 8 | 0.8750 | 1.0000 | 0.8750 | 0.8750 |
| work_order_business_urge | 6 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

### tp_work_order_business_complaint_val_004 (work_order_business_complaint)
- gold_track: task
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_active_task_slot_fill_val_000 (active_task_slot_fill)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_active_task_slot_fill_val_006 (active_task_slot_fill)
- gold_track: task
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_active_task_slot_fill_val_007 (active_task_slot_fill)
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
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_r3_ambiguous_all_null_val_008 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_ambiguous_all_null_val_011 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_ambiguous_all_null_val_017 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_active_task_slot_fill_val_010 (active_task_slot_fill)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_r3_active_task_slot_fill_val_016 (active_task_slot_fill)
- gold_track: task
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True
