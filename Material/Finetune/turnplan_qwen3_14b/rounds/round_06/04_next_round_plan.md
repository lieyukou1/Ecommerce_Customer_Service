# round_06 Next Round Plan

1. Do **not** immediately rerun the same QLoRA recipe with minor row additions.
2. Start from the round_06 locked facts:
   - minimized schema was real
   - contrast groups were real
   - result still lost to base
3. Re-open task definition at the supervision level, not the parser/output-contract level:
   - output contract stays `task / knowledge / chitchat / directive`
   - training objective may need a narrower or staged target
4. Before any round_07 training, answer two questions explicitly:
   - which business decisions are the base model already strong at and should not be destabilized?
   - which remaining error family is worth supervising directly because runtime cannot safely absorb it?
5. If a new round is approved, it should be meaningfully different in one of these dimensions:
   - objective decomposition
   - data balance strategy
   - loss surface / optimization strategy
   - evaluator target definition
