# round_05 Base vs Candidate Regression Analysis

## Summary

- total compared samples: `39`
- effective regressions: `3`
- effective gains: `1`
- non-net-output changes: `3`

## Change Family Counts

- `all_null_gain`: `1`
- `command_family_shift_without_net_success_change`: `1`
- `flow_shift_without_net_success_change`: `1`
- `slot_extraction_change_without_net_success_change`: `1`
- `task_to_all_null_regression`: `2`
- `task_to_exit_runtime_regression`: `1`

## Regressions

### tp_active_task_slot_fill_val_007
- bucket: `active_task_slot_fill`
- user_message: `可视对讲检修这个`
- change_family: `task_to_all_null_regression`
- base_track -> candidate_track: `task -> all_null`
- command_family_match: `True -> False`
- flow_match: `True -> True`
- effective_gate_pass: `True -> False`
- gold: `{"task": {"commands": [{"command": "set_slots", "slots": {"service_item_id": "SVC2008"}}]}, "knowledge": null, "chitchat": null, "directive": null}`
- base: `{"task": {"commands": [{"command": "set_slots", "slots": {"service_item_id": "SVC2008"}}]}, "knowledge": null, "chitchat": null, "directive": null}`
- candidate: `{"task": null, "knowledge": null, "chitchat": null, "directive": null}`

### tp_work_order_business_complaint_val_004
- bucket: `work_order_business_complaint`
- user_message: `这车位地锁报修了几次都没弄好，到底能不能解决了？`
- change_family: `task_to_all_null_regression`
- base_track -> candidate_track: `task -> all_null`
- command_family_match: `True -> False`
- flow_match: `True -> False`
- effective_gate_pass: `True -> False`
- gold: `{"task": {"commands": [{"command": "start_flow", "flow": "complaint_request_submission"}, {"command": "set_slots", "slots": {"work_order_id": "WO20260601009", "complaint_reason": "反复报修还没解决"}}]}, "knowledge": null, "chitchat": null, "directive": null}`
- base: `{"task": {"commands": [{"command": "start_flow", "flow": "complaint_request_submission"}, {"command": "set_slots", "slots": {"work_order_id": "WO20260601009", "complaint_reason": "车位地锁报修了几次都没弄好", "complaint_confirm": "确认"}}]}, "knowledge": null, "chitchat": null, "directive": null}`
- candidate: `{"task": null, "knowledge": null, "chitchat": null, "directive": null}`

### tp_task_interrupt_resume_cancel_val_006
- bucket: `task_interrupt_resume_cancel`
- user_message: `这个先停一下，我想改成投诉了，之前说好会上门，结果一直没来`
- change_family: `task_to_exit_runtime_regression`
- base_track -> candidate_track: `task -> directive`
- command_family_match: `False -> False`
- flow_match: `True -> False`
- effective_gate_pass: `True -> True`
- gold: `{"task": {"commands": [{"command": "start_flow", "flow": "complaint_request_submission"}, {"command": "set_slots", "slots": {"work_order_id": "WO20260601011", "complaint_reason": "说好上门又放了鸽子"}}]}, "knowledge": null, "chitchat": null, "directive": null}`
- base: `{"task": {"commands": [{"command": "cancel_flow"}, {"command": "start_flow", "flow": "complaint_request_submission"}, {"command": "set_slots", "slots": {"work_order_id": "WO20260601011", "complaint_reason": "之前说好会上门，结果一直没来"}}]}, "knowledge": null, "chitchat": null, "directive": null}`
- candidate: `{"task": null, "knowledge": null, "chitchat": null, "directive": {"action": "exit_runtime"}}`

## Gains

### tp_ambiguous_all_null_val_002
- bucket: `ambiguous_all_null`
- user_message: `我想把门锁密码处理一下`
- change_family: `all_null_gain`
- base_track -> candidate_track: `task -> all_null`
- gold: `{"task": null, "knowledge": null, "chitchat": null, "directive": null}`
- base: `{"task": {"commands": [{"command": "start_flow", "flow": "service_item_detail_query"}, {"command": "set_slots", "slots": {"service_item_id": "SVC2003"}}]}, "knowledge": null, "chitchat": null, "directive": null}`
- candidate: `{"task": null, "knowledge": null, "chitchat": null, "directive": null}`

## Non-Net Changes

### tp_task_interrupt_resume_cancel_val_002
- bucket: `task_interrupt_resume_cancel`
- user_message: `先别按催办处理了，我想直接投诉，这事已经影响正常进出了`
- change_family: `command_family_shift_without_net_success_change`
- command_family_match: `False -> True`
- flow_match: `True -> True`
- slot_match: `False -> False`

### tp_task_interrupt_resume_cancel_val_004
- bucket: `task_interrupt_resume_cancel`
- user_message: `那现在说吧，那个催办的单子，继续填原因`
- change_family: `flow_shift_without_net_success_change`
- command_family_match: `False -> False`
- flow_match: `False -> True`
- slot_match: `False -> False`

### tp_active_task_slot_fill_val_001
- bucket: `active_task_slot_fill`
- user_message: `家里老人怕热，能快点处理吗`
- change_family: `slot_extraction_change_without_net_success_change`
- command_family_match: `True -> True`
- flow_match: `True -> True`
- slot_match: `False -> True`

