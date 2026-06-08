# TurnPlan Phase 1 AI Audit

## Overview

- train_records: 450
- val_records: 80
- total_records: 530
- unique_input_label_pairs: 530
- duplicate_pairs: 0
- unique_user_messages: 511
- unique_histories: 109

## Flow Coverage

- `work_order_status_query`: 18
- `service_progress_tracking`: 17
- `service_item_detail_query`: 17
- `resident_work_orders_list_query`: 17
- `resident_service_items_list_query`: 16
- `resident_rule_qa`: 16
- `work_order_urge_submission`: 61
- `complaint_request_submission`: 48

## Knowledge Intent Coverage

- `service_item_info`: 25
- `work_order_info`: 24
- `property_fee_rule`: 12
- `renovation_filing_rule`: 12
- `parking_rule`: 11
- `pet_rule`: 11
- `community_rule`: 11
- `general_property_info`: 11

## Context Coverage

- active_task_records: 133
- active_system_task_records: 66
- paused_task_records: 22
- multi_slot_set_slots_records: 102
- contact_phone_slot_records: 23
- complaint_confirm_negative_records: 15
- conversation_state_distribution: `{"IDLE": 188, "FOCUSED_KNOWLEDGE": 193, "ACTIVE_TASK": 133, "CLARIFYING": 8, "TRANSITIONING": 8}`
- history_length_distribution: `{"0": 185, "2": 128, "4": 124, "6": 93}`

## SFT Ready Audit

- sft_ready_pass_rate: 0.8358
- language_naturalness_pass_rate: 0.8943
- history_state_consistency_pass_rate: 0.9340
- object_slot_consistency_pass_rate: 0.9925

## SFT Contract Checks

- mentions_intents_array: True
- mentions_flow_field: True
- mentions_active_system_task: True
