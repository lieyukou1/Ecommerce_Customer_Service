# reduced_round03_curated_v1 Summary

- source dataset: `reduced_round03_aug_v1`
- purpose: remove wrong-bucket / slot-drift outliers before round_03 training

| bucket | train_actual | train_target | val_actual | val_target |
| --- | ---: | ---: | ---: | ---: |
| `ambiguous_all_null` | 80 | 80 | 20 | 20 |
| `active_task_slot_fill` | 73 | 80 | 20 | 20 |
| `task_interrupt_resume_cancel` | 74 | 80 | 20 | 20 |
| `directive_exit_runtime` | 40 | 40 | 10 | 10 |
| `work_order_business_urge` | 30 | 30 | 6 | 8 |
| `work_order_business_complaint` | 30 | 30 | 8 | 8 |

- total_records: `411`
- dropped_records: `15`
- patched_records: `10`

## Dropped IDs

- `tp_active_task_slot_fill_train_016`
- `tp_active_task_slot_fill_train_044`
- `tp_r3_active_task_slot_fill_train_056`
- `tp_r3_active_task_slot_fill_train_064`
- `tp_r3_active_task_slot_fill_train_076`
- `tp_r3_active_task_slot_fill_train_078`
- `tp_r3_active_task_slot_fill_train_079`
- `tp_r3_task_interrupt_resume_cancel_train_047`
- `tp_r3_task_interrupt_resume_cancel_train_054`
- `tp_r3_task_interrupt_resume_cancel_train_060`
- `tp_r3_task_interrupt_resume_cancel_train_064`
- `tp_r3_task_interrupt_resume_cancel_train_069`
- `tp_r3_task_interrupt_resume_cancel_train_076`
- `tp_r3_work_order_business_urge_val_005`
- `tp_r3_work_order_business_urge_val_007`

## Patched IDs

- `tp_directive_exit_runtime_train_007`
- `tp_active_task_slot_fill_train_023`
- `tp_active_task_slot_fill_train_035`
- `tp_r3_active_task_slot_fill_train_054`
- `tp_r3_active_task_slot_fill_train_055`
- `tp_r3_active_task_slot_fill_train_060`
- `tp_r3_active_task_slot_fill_train_066`
- `tp_r3_active_task_slot_fill_train_070`
- `tp_active_task_slot_fill_val_009`
- `tp_r3_active_task_slot_fill_val_013`
