# reduced_round04_keep_base_v1 Summary

- source dataset: `canonical_llm`
- purpose: keep-only reduced base after audit gating, before targeted repair and bucket rebuild are added back.

| bucket | train | val |
| --- | ---: | ---: |
| `task_interrupt_resume_cancel` | 45 | 7 |
| `work_order_business_urge` | 30 | 5 |
| `work_order_business_complaint` | 30 | 5 |

- train_total: `105`
- val_total: `17`

Excluded on purpose:

- `active_task_slot_fill`: moved to targeted-fix queue
- `ambiguous_all_null`: moved to bucket-rebuild queue
- `directive_exit_runtime`: moved to bucket-rebuild queue
