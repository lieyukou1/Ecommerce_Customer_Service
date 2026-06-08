# round_06 Problem Analysis

## First-Pass Conclusion

This round answered one important question cleanly:

- after removing the old export leakage
- and after adding explicit same-utterance contrast groups

the unified Planner SFT candidate still does not beat the untouched base model.

So the old diagnosis must now be tightened:

- round_05 was partially confounded by a bad export
- round_06 removed that confound
- the negative result remained

That means the remaining blocker is not just dirty export mechanics.

## What This Round Successfully Ruled Out

### 1. The failure is not mainly caused by raw-input leakage

This round used:

- sanitized planner input only
- no `runtime_state.last_route.track`
- no answer-like focused object attributes in SFT user payload

Yet the candidate still regressed.

So the previous failure cannot be explained away as:

- "the model was confused by old schema leakage, once removed it will naturally recover"

That did not happen.

### 2. The failure is not mainly caused by missing contrast rows in the exact targeted mechanisms

This round explicitly added train-only contrast groups for:

- `community_rule` knowledge vs active task slot fill
- `service_item_info` knowledge vs active task slot fill
- `cancel_flow` vs `exit_runtime`
- deictic complaint with focused object vs no object context

Those were not just conceptual plans anymore; they were instantiated records and passed audit.

Yet the candidate still regressed on nearby business buckets.

So the previous failure cannot be reduced to:

- "we just forgot to add the hard pairs"

We added them, and the model still did not improve.

## Metric-Level Result

Compared with the base model on the identical `39`-sample val set:

- `top_level_track_accuracy`: `0.8205 -> 0.7692`
- `task_command_family_accuracy`: `0.7778 -> 0.7407`
- `flow_selection_accuracy`: `0.9333 -> 0.8000`
- `slot_fill_exact_match`: `0.2174 -> 0.2174`
- `adjusted_protocol_gate_pass_rate`: `0.9231 -> 0.8462`

The key signal is not one isolated metric. It is the pattern:

- nothing important recovered above base
- one metric stayed flat
- several core task metrics dropped again

## Failure Shape

The bucket pattern stayed structurally similar to round_05:

- `directive_exit_runtime` remains easy
- `work_order_business_urge` remains easy
- the hard regressions stay concentrated in:
  - `active_task_slot_fill`
  - `task_interrupt_resume_cancel`
  - `work_order_business_complaint`

That is a very specific pattern:

- the model is not generally broken
- it is specifically weaker where meaning depends on current business state and protocol action choice

## What the Contrastive Repair Did Not Achieve

### 1. `active_task short phrase -> set_slots` still did not become stronger than base

This was one of the main intended repairs.

The expectation was:

- same noun phrase
- active task present
- explicit slot-filling gold

should become a harder signal than the base model's default semantic reading.

But `active_task_slot_fill` stayed below base:

- base bucket track accuracy: `0.9`
- round_06 candidate: `0.8`

This is the clearest sign that state-conditioned continuation meaning is still not being learned strongly enough.

### 2. `cancel_flow` vs `exit_runtime` remains entangled

This was another explicitly targeted repair.

But `task_interrupt_resume_cancel` remained below base:

- base bucket track accuracy: `0.7143`
- round_06 candidate: `0.5714`

The training signal did not successfully separate:

- stop the current complaint flow
- exit the current runtime topic
- stop talking for now

Those behaviors are still clustering together too coarsely.

### 3. Object-conditioned complaint start is still not stably stronger than caution

The complaint object contrast pairs were meant to teach:

- same phrase with object context -> complaint task
- same phrase without object context -> `all_null`

But `work_order_business_complaint` still regressed:

- base bucket track accuracy: `1.0`
- round_06 candidate: `0.8`

So the model is still overpaying for conservative fallback in a place where the base model already had a stronger natural prior.

## Stronger Root-Cause Statement After round_06

At this point the working hypothesis should be upgraded:

- the problem is no longer "data is dirty"
- and no longer "we forgot the contrast rows"

The stronger problem is:

- the current SFT target is trying to push a relatively small supervision set against a stronger base semantic prior
- and the base prior is already quite good on several of these business decisions
- the LoRA update is not selectively strengthening the hard protocol distinctions; it is also disturbing existing good judgment

In plainer language:

- we are not only failing to teach the missing rule
- we are also unteaching part of what the base already knew

## Practical Meaning

This round does **not** prove that Planner SFT is impossible.

It does prove something narrower but important:

- "same recipe, cleaner data, more contrast rows" is still not enough

So the next move cannot honestly be:

- add a few more pairs
- rerun the same 2-epoch QLoRA
- hope this time it flips

That would no longer be an evidence-based plan.
