# round_05 Decision Log

## Locked Facts

- reduced round_04 candidate can be trained, merged, and replayed end to end
- the training infrastructure is no longer the blocker
- this specific reduced SFT candidate is not promotable
- round_05 uncovered a real export bug:
  - reduced export bypassed the planner input sanitizer
  - so the previous run was not a pure minimized-schema experiment

## Not Locked Yet

- whether the main problem is still supervision target design
- whether the reduced slice is too small / too narrow
- whether the hardest remaining error mechanism should be learned by SFT at all
