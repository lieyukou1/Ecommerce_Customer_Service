# reduced_round04 Triage Notes

## 结论

这次 reduced 数据不再按“全部混在一起修”走，而是拆成三类：

- `keep`
- `targeted_fix`
- `bucket_rebuild`

## 三类规模

- `keep = 122`
- `targeted_fix = 60`
- `bucket_rebuild = 82`

## keep

保留桶：

- `task_interrupt_resume_cancel`
- `work_order_business_urge`
- `work_order_business_complaint`

这批样本已经切成新的 keep-only 底盘：

- train `105`
- val `17`

## targeted_fix

当前只有一个桶：

- `active_task_slot_fill`

它的问题不是脏，而是虽然审计通过，仍然是 runtime 回放里最容易回退的主桶，所以要单独做 focused repair。

## bucket_rebuild

这一类不建议逐条缝：

- `ambiguous_all_null`
- `directive_exit_runtime`

原因：

- `ambiguous_all_null` 还残留模板痕迹和 clarify 边界噪声
- `directive_exit_runtime` 仍有大量 lead-in / timeline 问题

## 下一步动作

1. 先拿 `keep` 做稳定底盘
2. 单独修 `active_task_slot_fill`
3. 整桶重做 `ambiguous_all_null` 和 `directive_exit_runtime`
4. 再合并成下一版 reduced 候选训练集
