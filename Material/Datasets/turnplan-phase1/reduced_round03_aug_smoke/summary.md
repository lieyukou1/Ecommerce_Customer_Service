# reduced_round03_aug_smoke Summary

- source base: `reduced_round03_base_v1`
- purpose: reduced `round_03` augmented dataset for focused SFT retry

| bucket | train_actual | train_target | val_actual | val_target |
| --- | ---: | ---: | ---: | ---: |
| `ambiguous_all_null` | 36 | 80 | 7 | 20 |
| `active_task_slot_fill` | 51 | 80 | 11 | 20 |
| `task_interrupt_resume_cancel` | 46 | 80 | 8 | 20 |
| `directive_exit_runtime` | 36 | 40 | 7 | 10 |
| `work_order_business_urge` | 30 | 30 | 6 | 8 |
| `work_order_business_complaint` | 30 | 30 | 6 | 8 |

- total_records: `274`
- train_total: `229`
- val_total: `45`

## Model Health

- `xinglian_openai` / `gpt-5.4-mini`: `HTTP Error 403: Forbidden`
- `project_deepseek` / `deepseek-v4-flash`: `ok`
