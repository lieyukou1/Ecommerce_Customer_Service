# reduced_round04_directive_exit_runtime_rebuild_v1 Summary

- source dataset: `canonical_llm`
- purpose: rebuild exit-runtime samples so every exit has believable runtime lead-in.

- total_records: `41`
- split_counts: `{'train': 35, 'val': 6}`

## State counts

- `ACTIVE_TASK`: `27`
- `FOCUSED_KNOWLEDGE`: `14`

## Flow counts

- `complaint_request_submission`: `7`
- `focused_knowledge`: `14`
- `work_order_status_query`: `7`
- `work_order_urge_submission`: `13`

## Rebuild focus

- add concrete lead-in before every `exit_runtime`
- keep exit language short and natural
- separate knowledge-context exits from active-task exits
