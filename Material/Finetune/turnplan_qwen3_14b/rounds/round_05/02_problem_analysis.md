# round_05 Problem Analysis

## First-Pass Conclusion

This round successfully validated the mechanics of the reduced training pipeline:

- reduced dataset export works
- QLoRA training completes on the 4090 without OOM
- adapter merge works
- base and candidate can both be served through vLLM and replayed with the real runtime evaluator

But the model result is still negative:

- the candidate is worse than the untouched base model on the reduced round_04 val replay

## Immediate Failure Shape

- `ambiguous_all_null` improved slightly on top-level track accuracy: `0.3333 -> 0.5000`
- but core task execution judgment regressed:
  - `active_task_slot_fill`: `0.9 -> 0.8`
  - `task_interrupt_resume_cancel`: `0.7143 -> 0.5714`
  - `work_order_business_complaint`: `1.0 -> 0.8`

That means this round did not fail because the pipeline is broken. It failed because the current supervision signal still does not produce a better Planner than the base model.

## Base vs Candidate Change Map

- detailed diff:
  - [round05_base_vs_candidate_regressions.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_05/artifacts/round05_base_vs_candidate_regressions.md)
  - [round05_base_vs_candidate_regressions.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_05/artifacts/round05_base_vs_candidate_regressions.json)

The per-sample comparison is more informative than the headline metric drop:

- effective regressions: `3`
- effective gains: `1`
- the only gain is:
  - `ambiguous_all_null`: base mistakenly started a task, candidate returned `all_null`
- the three regressions are:
  - `task -> all_null` on `active_task_slot_fill`
  - `task -> all_null` on `work_order_business_complaint`
  - `task -> exit_runtime` on `task_interrupt_resume_cancel`

This is the clearest signal of this round:

- candidate got slightly better at being conservative
- but it spent that gain by refusing or exiting real task continuations

## Mechanism-Level Diagnosis

### 1. Conservative fallback is being over-activated

Evidence:

- improved sample:
  - `我想把门锁密码处理一下` moved from mistaken `task` to correct `all_null`
- regressed samples:
  - `可视对讲检修这个` moved from correct `set_slots` to `all_null`
  - `这车位地锁报修了几次都没弄好，到底能不能解决了？` moved from correct complaint start to `all_null`
  - `这个先停一下，我想改成投诉了，之前说好会上门，结果一直没来` moved from complaint switch to `exit_runtime`

Interpretation:

- the reduced SFT did teach the model to hesitate more
- but that hesitation spilled into business-task continuation and switch scenarios

### 2. Active-task state is still not beating the base model's natural semantics

Persistent hard cases:

- `我想问社区公约`
- `可视对讲检修这个`

In both cases the gold label is not standalone `knowledge`; it is task-side slot filling under an already active flow:

- `resident_rule_qa.collect_rule_topic -> set_slots(rule_topic)`
- `service_item_detail_query.collect_service_item_id -> set_slots(service_item_id)`

Base and candidate both still want to treat these short noun phrases as standalone semantic requests instead of continuation payloads. That means:

- keeping `active_task` in the input is not enough by itself
- the current contrast signal is still too weak to force "same utterance, different meaning because the state changed"

### 3. `cancel_flow` vs `exit_runtime` is still entangled

Persistent failures:

- `算了，投诉那个先不弄了`
- `算了，这个投诉先放放，不弄了`

Both base and candidate map them to `directive.exit_runtime`, while gold is `task.cancel_flow`.

This boundary was already known before round_05, and round_05 did not really fix it. Candidate also regressed on a nearby switch sample:

- `这个先停一下，我想改成投诉了...` -> `exit_runtime`

So the model is still clustering:

- stop current task
- leave current runtime topic
- stop talking for now

into one coarse "exit" behavior.

### 4. Reduced data is clean enough, but still not sharp enough

The reduced slice is no longer suffering from the old high-noise problems:

- no duplicate pair problem
- no obvious template residue problem
- no obvious cross-field contradiction problem in the audited slice

But round_05 shows a different limit:

- cleanliness alone did not create a strong enough supervision target
- once noisy samples were removed, the remaining problem became semantic tension, not data hygiene

## Two Broken Assumptions Found After round_05

### A. round_05 export did not actually use the minimized planner input

We found a pipeline bug in:

- [prepare_reduced_round04_training_assets.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/prepare_reduced_round04_training_assets.py)

Before the fix, the round_04 export path was still dumping raw `record["input"]` into SFT messages instead of the sanitized planner schema. That means round_05 training still saw:

- `runtime_state.last_route.track`
- answer-like `focused_object.attributes.status / amount / summary / price / description`

So round_05 was not a pure test of:

- reduced data
- plus minimized planner schema

It was still polluted by part of the old input contract.

This matters because it weakens any conclusion of the form:

- "we already tested the new schema and it still failed"

We did not fully test that yet.

### B. contrast groups were specified in principle, but not instantiated in the data

In `reduced_round04_candidate_v1`, `semantic_meta.contrast_group` is effectively empty for the train split.

That means we still do not have a deliberate same-utterance contrast curriculum such as:

- same short noun phrase
  - with active task -> `set_slots`
  - without active task -> `knowledge` or `all_null`
- same "先不弄了" family
  - under active complaint task -> `cancel_flow`
  - as topic exit -> `directive.exit_runtime`

This is important because the main remaining failure is exactly state-conditioned meaning shift. The dataset is cleaner now, but it is not yet contrastive in the way this task requires.
