# round_06 Decision Log

## Locked Facts

- round_06 was a real validation of the corrected minimized-schema export
- round_06 did contain explicit contrastive train pairs
- the val set stayed identical to round_04, so comparison against base is fair
- the candidate still failed to beat base on core Planner metrics

## Explanations We Keep

- the remaining issue is not mainly export leakage anymore
- the remaining issue is not mainly "forgot to add contrast groups"
- the current unified Planner SFT recipe is still disturbing base judgment more than it is adding reliable protocol skill

## Explanations We Reject

- "round_05 was invalid, so round_06 will naturally recover once export is fixed"
- "just adding a few same-utterance pairs is sufficient to flip the result"
- "this is now primarily a training infrastructure problem"

## Final Read of round_06

round_06 is a clean negative experiment:

- it reduces uncertainty
- it narrows the real design problem
- it does not justify promotion

That makes it a useful round, even though the model result is still negative.

## What This Means for the Next Step

The next step should be a design change, not another nearly identical rerun.

The most defensible next discussion topics are:

1. whether the current gold target is over-constraining task/knowledge/action boundaries in a way the base prior resists
2. whether the remaining hard abilities should be separated into a narrower supervision target
3. whether active-task continuation and clarify/caution behavior need a different data balance or a different objective shape rather than just more rows
