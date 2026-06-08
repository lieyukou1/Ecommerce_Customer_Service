# reduced_round06_contrastive_candidate_v1 Summary

- source dataset: `reduced_round04_candidate_v1`
- purpose: add state-conditioned contrast groups before the next reduced Planner SFT run.

- total_records: `288`
- added_contrastive_train_records: `24`

| bucket | train | val |
| --- | ---: | ---: |
| `active_task_slot_fill` | 56 | 10 |
| `ambiguous_all_null` | 37 | 6 |
| `directive_exit_runtime` | 39 | 6 |
| `service_item_knowledge` | 6 | 0 |
| `task_interrupt_resume_cancel` | 49 | 7 |
| `work_order_business_complaint` | 32 | 5 |
| `work_order_business_urge` | 30 | 5 |

## Contrast Groups

- `contrast_cancel_exit_01`: `2` rows
- `contrast_cancel_exit_02`: `2` rows
- `contrast_cancel_exit_03`: `2` rows
- `contrast_cancel_exit_04`: `2` rows
- `contrast_community_rule_01`: `2` rows
- `contrast_community_rule_02`: `2` rows
- `contrast_community_rule_03`: `2` rows
- `contrast_complaint_object_01`: `2` rows
- `contrast_complaint_object_02`: `2` rows
- `contrast_service_item_01`: `2` rows
- `contrast_service_item_02`: `2` rows
- `contrast_service_item_03`: `2` rows
