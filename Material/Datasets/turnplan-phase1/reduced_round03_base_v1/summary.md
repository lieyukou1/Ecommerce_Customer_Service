# reduced_round03_base_v1 Summary

- source: `turnplan-phase1 / canonical_llm`
- purpose: reduced `round_03` base slice before targeted augmentation

## Selected Buckets

- `ambiguous_all_null`
- `active_task_slot_fill`
- `task_interrupt_resume_cancel`
- `directive_exit_runtime`
- `work_order_business_urge`
- `work_order_business_complaint`

## Excluded Buckets

- `work_order_read_only_task`
- `service_item_knowledge`
- `object_context_followup`
- `chitchat`

## Counts

| bucket | train_actual | train_target | val_actual | val_target |
| --- | ---: | ---: | ---: | ---: |
| `ambiguous_all_null` | 35 | 80 | 6 | 20 |
| `active_task_slot_fill` | 50 | 80 | 10 | 20 |
| `task_interrupt_resume_cancel` | 45 | 80 | 7 | 20 |
| `directive_exit_runtime` | 35 | 40 | 6 | 10 |
| `work_order_business_urge` | 30 | 30 | 5 | 8 |
| `work_order_business_complaint` | 30 | 30 | 5 | 8 |

- train_total: `225`
- val_total: `39`

## Validation

- checked_records: `264`
- validation_errors: `0`
