# TurnPlan Phase 1 AI 审计报告

## 总览

- 训练集：450
- 验证集：80
- 全量样本：530
- 唯一 input+label 对：530
- 精确重复对：0
- 唯一 user_message：526
- 唯一 history：346

## Flow 覆盖

- `work_order_status_query`: 18
- `service_progress_tracking`: 17
- `service_item_detail_query`: 17
- `resident_work_orders_list_query`: 17
- `resident_service_items_list_query`: 16
- `resident_rule_qa`: 16
- `work_order_urge_submission`: 61
- `complaint_request_submission`: 48

## Knowledge Intent 覆盖

- `service_item_info`: 25
- `work_order_info`: 24
- `property_fee_rule`: 12
- `renovation_filing_rule`: 12
- `parking_rule`: 11
- `pet_rule`: 11
- `community_rule`: 11
- `general_property_info`: 11

## 状态与上下文覆盖

- active_task 记录数：133
- active_system_task 记录数：66
- paused_tasks 非空记录数：22
- 多槽位 set_slots 记录数：102
- `contact_phone` 槽位记录数：23
- `complaint_confirm` 否定样本数：15
- conversation_state 分布：`{"IDLE": 188, "FOCUSED_KNOWLEDGE": 193, "ACTIVE_TASK": 133, "CLARIFYING": 8, "TRANSITIONING": 8}`
- history 长度分布：`{"0": 185, "2": 128, "4": 124, "6": 93}`

## SFT 合同检查

- `intents` 数组格式说明：True
- `flow` 字段说明：True
- `active_system_task` 规则说明：True
