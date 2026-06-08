# round_05 Next Round Plan

1. Re-export `reduced_round04_candidate_v1` with sanitized planner input only.
2. Rebuild the reduced set around failure mechanisms, not bucket names:
   - `task continuation must not collapse to all_null`
   - `cancel_flow vs exit_runtime`
   - `active_task short noun phrase -> set_slots`
3. Add explicit contrast groups:
   - same utterance under `ACTIVE_TASK` vs `IDLE`
   - same `先不弄了` family under `cancel_flow` vs `exit_runtime`
   - same service/rule noun phrase under `knowledge` vs `active_task slot fill`
4. Keep the current output contract unchanged:
   - still only `task / knowledge / chitchat / directive`
5. Only retrain after the new export passes two checks:
   - no leaked `last_route.track`
   - no answer-like focused object fields in SFT input
