# reduced_round03_curated_v1 Augmentation Gaps

- purpose: targeted augmentation todo after base slice extraction

| bucket | train_actual | train_target | train_gap | val_actual | val_target | val_gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `ambiguous_all_null` | 80 | 80 | 0 | 20 | 20 | 0 |
| `active_task_slot_fill` | 73 | 80 | 7 | 20 | 20 | 0 |
| `task_interrupt_resume_cancel` | 74 | 80 | 6 | 20 | 20 | 0 |
| `directive_exit_runtime` | 40 | 40 | 0 | 10 | 10 | 0 |
| `work_order_business_urge` | 30 | 30 | 0 | 6 | 8 | 2 |
| `work_order_business_complaint` | 30 | 30 | 0 | 8 | 8 | 0 |

## Priority

1. `ambiguous_all_null`
2. `task_interrupt_resume_cancel`
3. `active_task_slot_fill`
4. `directive_exit_runtime`
5. `work_order_business_urge` / `work_order_business_complaint` val-only 补齐
