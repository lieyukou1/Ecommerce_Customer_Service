# reduced_round03_base_v1 Augmentation Gaps

- purpose: targeted augmentation todo after base slice extraction

| bucket | train_actual | train_target | train_gap | val_actual | val_target | val_gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `ambiguous_all_null` | 35 | 80 | 45 | 6 | 20 | 14 |
| `active_task_slot_fill` | 50 | 80 | 30 | 10 | 20 | 10 |
| `task_interrupt_resume_cancel` | 45 | 80 | 35 | 7 | 20 | 13 |
| `directive_exit_runtime` | 35 | 40 | 5 | 6 | 10 | 4 |
| `work_order_business_urge` | 30 | 30 | 0 | 5 | 8 | 3 |
| `work_order_business_complaint` | 30 | 30 | 0 | 5 | 8 | 3 |

## Priority

1. `ambiguous_all_null`
2. `task_interrupt_resume_cancel`
3. `active_task_slot_fill`
4. `directive_exit_runtime`
5. `work_order_business_urge` / `work_order_business_complaint` val-only 补齐
