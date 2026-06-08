# reduced_round04_active_task_slot_fill_repair_v1 Summary

- source dataset: `canonical_llm`
- purpose: repair active-task slot-fill samples by strengthening task lead-in and slot-target alignment.

- total_records: `60`

| split:slot | count |
| --- | ---: |
| `train:complaint_confirm` | 7 |
| `train:complaint_reason` | 7 |
| `train:contact_phone` | 14 |
| `train:rule_topic` | 7 |
| `train:service_item_id` | 7 |
| `train:urge_reason` | 8 |
| `val:complaint_confirm` | 1 |
| `val:complaint_reason` | 2 |
| `val:contact_phone` | 2 |
| `val:rule_topic` | 1 |
| `val:service_item_id` | 2 |
| `val:urge_reason` | 2 |

## Repair focus

- strengthen `history -> active_task -> current slot fill` continuity
- keep short continuation utterances, but make the lead-in explicit enough to be learnable
- preserve cancel-vs-confirm contrast inside `complaint_confirm`
