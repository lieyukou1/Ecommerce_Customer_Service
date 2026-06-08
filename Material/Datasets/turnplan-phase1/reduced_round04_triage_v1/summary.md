# reduced_round04_triage_v1 Summary

- source dataset: `canonical_llm`
- purpose: classify reduced round_04 work into keep / targeted_fix / bucket_rebuild.

## keep

- description: Audit-clean and structurally aligned rows that can stay as the next reduced training base.
- total_records: `122`

| bucket | train | val | sft_ready | not_ready |
| --- | ---: | ---: | ---: | ---: |
| `task_interrupt_resume_cancel` | 45 | 7 | 52 | 0 |
| `work_order_business_complaint` | 30 | 5 | 35 | 0 |
| `work_order_business_urge` | 30 | 5 | 35 | 0 |

## targeted_fix

- description: Rows that are on the right task line but still need focused repair before final training.
- total_records: `60`

| bucket | train | val | sft_ready | not_ready |
| --- | ---: | ---: | ---: | ---: |
| `active_task_slot_fill` | 50 | 10 | 60 | 0 |

Focused rationale:

- `active_task_slot_fill` is audit-clean, but still remains a known regression-prone bucket in runtime replay.

## bucket_rebuild

- description: Systemically noisy buckets that should be rebuilt as a group instead of patched row by row.
- total_records: `82`

| bucket | train | val | sft_ready | not_ready |
| --- | ---: | ---: | ---: | ---: |
| `ambiguous_all_null` | 35 | 6 | 33 | 8 |
| `directive_exit_runtime` | 35 | 6 | 14 | 27 |

Focused rationale:

- `ambiguous_all_null` still contains template residue and clarify-boundary noise.
- `directive_exit_runtime` still has timeline lead-in problems and should be rebuilt as a group.

Top audit notes:

- `timeline: active task exists but history has no lead-in context`: `35`

## Notes

- `work_order_read_only_task` is intentionally left out of this reduced training triage because high-loss read-only handling is currently absorbed by runtime compatibility logic.
- targeted-fix buckets: `active_task_slot_fill`
