# TurnPlan Runtime Eval - deepseek_v4_flash_reduced_round04_candidate_train_20260607a

- total: 225
- all_null_clarify_fallback_count: 10
- effective_failure_records: 39
- top_level_track_accuracy: 0.8311
- directive_accuracy: 0.8571
- all_null_accuracy: 0.3143
- knowledge_intent_accuracy: 0.0000
- task_command_family_accuracy: 0.8194
- flow_selection_accuracy: 0.9574
- slot_fill_exact_match: 0.2615
- knowledge_false_positive_rate: 0.0000
- json_valid_rate: 1.0000
- protocol_gate_pass_rate: 0.9333
- adjusted_protocol_gate_pass_rate: 0.9778

## High-Loss Read-Only

- count: 0
- system_success_rate: 0.0000
- list_query_success_rate: 0.0000
- work_order_runtime_success_rate: 0.0000
- service_item_detail_success_rate: 0.0000

## Buckets

| bucket | count | track_acc | json_valid | gate_pass | adjusted_gate_pass |
| --- | ---: | ---: | ---: | ---: | ---: |
| active_task_slot_fill | 50 | 0.9600 | 1.0000 | 0.9800 | 0.9800 |
| ambiguous_all_null | 35 | 0.3143 | 1.0000 | 0.6286 | 0.9143 |
| directive_exit_runtime | 35 | 0.8571 | 1.0000 | 1.0000 | 1.0000 |
| task_interrupt_resume_cancel | 45 | 0.8444 | 1.0000 | 0.9778 | 0.9778 |
| work_order_business_complaint | 30 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| work_order_business_urge | 30 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

## Sample Failures

### tp_task_interrupt_resume_cancel_train_001 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_task_interrupt_resume_cancel_train_005 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_task_interrupt_resume_cancel_train_009 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_task_interrupt_resume_cancel_train_013 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_task_interrupt_resume_cancel_train_014 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: task
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False
- parse_error: `TypeError: StartFlowCommand.__init__() got an unexpected keyword argument 'slots'`

### tp_task_interrupt_resume_cancel_train_025 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_task_interrupt_resume_cancel_train_033 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_task_interrupt_resume_cancel_train_037 (task_interrupt_resume_cancel)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_active_task_slot_fill_train_005 (active_task_slot_fill)
- gold_track: task
- pred_track: all_null
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False

### tp_active_task_slot_fill_train_016 (active_task_slot_fill)
- gold_track: task
- pred_track: directive
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_000 (ambiguous_all_null)
- gold_track: all_null
- pred_track: knowledge
- json_valid: True
- protocol_gate_accepted: True
- effective_gate_pass: True

### tp_ambiguous_all_null_train_001 (ambiguous_all_null)
- gold_track: all_null
- pred_track: task
- json_valid: True
- protocol_gate_accepted: False
- effective_gate_pass: False
