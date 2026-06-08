# reduced_round04_ambiguous_all_null_rebuild_v1 Summary

- source dataset: `canonical_llm`
- purpose: rebuild ambiguous clarify-trigger samples with natural wording and timeline-consistent context.

- total_records: `41`
- split_counts: `{'train': 35, 'val': 6}`

| state | count |
| --- | ---: |
| `IDLE` | 9 |
| `CLARIFYING` | 8 |
| `FOCUSED_KNOWLEDGE` | 8 |
| `ACTIVE_TASK` | 8 |
| `TRANSITIONING` | 8 |

## Scenario coverage

- `community_invoice`: `8`
- `door_lock_password`: `21`
- `doorplate_name`: `7`
- `neighbor_renovation`: `5`

## Rebuild focus

- remove template residue and fake helper phrasing
- keep ambiguity genuine: user asks for something, but the flow is still underdetermined
- restore state-specific lead-in so `all_null / clarify fallback` is tied to believable context
