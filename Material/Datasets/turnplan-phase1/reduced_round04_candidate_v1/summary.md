# reduced_round04_candidate_v1 Summary

- source datasets: `reduced_round04_keep_base_v1, reduced_round04_active_task_slot_fill_repair_v1, reduced_round04_ambiguous_all_null_rebuild_v1, reduced_round04_directive_exit_runtime_rebuild_v1`
- purpose: assemble the reduced round_04 candidate after keep/fix/rebuild passes.

- total_records: `264`
- sft_ready_records: `264`
- unsafe_records: `0`

| bucket | train | val |
| --- | ---: | ---: |
| `active_task_slot_fill` | 50 | 10 |
| `ambiguous_all_null` | 35 | 6 |
| `directive_exit_runtime` | 35 | 6 |
| `task_interrupt_resume_cancel` | 45 | 7 |
| `work_order_business_complaint` | 30 | 5 |
| `work_order_business_urge` | 30 | 5 |