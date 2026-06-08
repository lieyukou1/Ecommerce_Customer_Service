# reduced_round03_aug_v1 Summary

- source base: `reduced_round03_base_v1`
- purpose: reduced `round_03` augmented dataset for focused SFT retry

| bucket | train_actual | train_target | val_actual | val_target |
| --- | ---: | ---: | ---: | ---: |
| `ambiguous_all_null` | 80 | 80 | 20 | 20 |
| `active_task_slot_fill` | 80 | 80 | 20 | 20 |
| `task_interrupt_resume_cancel` | 80 | 80 | 20 | 20 |
| `directive_exit_runtime` | 40 | 40 | 10 | 10 |
| `work_order_business_urge` | 30 | 30 | 8 | 8 |
| `work_order_business_complaint` | 30 | 30 | 8 | 8 |

- total_records: `426`
- train_total: `340`
- val_total: `86`

## Model Health

- `xinglian_openai` / `gpt-5.4-mini`: `HTTP Error 403: Forbidden`
- `project_deepseek` / `deepseek-v4-flash`: `ok`
