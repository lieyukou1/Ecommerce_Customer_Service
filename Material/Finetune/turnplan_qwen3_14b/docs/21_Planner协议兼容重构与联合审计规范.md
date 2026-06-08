# Planner 协议兼容重构与联合审计规范

- 最后更新时间：2026-06-07
- 适用范围：`TurnPlan` 数据集、离线导出链路、runtime 协议兼容层
- 关联轮次：[round_04](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/00_run_manifest.md)

## 1. 这次重构改了什么

这次没有改后端最终吃到的 `TurnPlan JSON` 合同。

最终输出仍然只有四条顶层轨道：

- `task`
- `knowledge`
- `chitchat`
- `directive`

真正变化的是三层：

1. `runtime` 里把高损失 `read_only` 逻辑从 `TurnPlanNormalizer` 内嵌判断，收敛成独立兼容层 [read_only_resolver.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/read_only_resolver.py)
2. 数据导出前对训练输入做最小化清洗，减少旧协议泄漏和答案泄漏：[input_sanitizer.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/input_sanitizer.py)
3. 数据不再只看 `user_message` 自然不自然，而是加上“语言 + 时间线 + 状态 + 对象 + 槽位”的联合审计：[audit_rules.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/audit_rules.py)

## 2. 后端职责怎么重新切开的

### 2.1 Planner 仍然只调用一次

没有改成两次 LLM 调用。

当前链路仍然是：

1. Planner 产出旧合同 `TurnPlan`
2. Protocol gate 调用 [turn_plan_normalizer.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/turn_plan_normalizer.py)
3. `TurnPlanNormalizer` 只负责：
   - 退出规则归一
   - 调 `ReadOnlyResolver`
   - 返回兼容后的 `TurnPlan`
4. Validator / gate / 执行链继续吃旧 shape

### 2.2 `read_only` 逻辑没有删除，而是正名

短期内它不再被视为“补锅脚本”，而是兼容期正式分流层：

- 高损失 `read_only` 优先保业务正确
- 低损失 `read_only` 继续留给模型做统一语义判断

## 3. 训练输入现在认什么字段

导出到 SFT 前，输入会被收缩为：

```json
{
  "history": [{"role": "user|assistant", "text": "..."}],
  "runtime_state": {
    "conversation_state": "...",
    "last_route": {"semantic_kind": "..."},
    "last_task_outcome": {"semantic_kind": "...", "flow_id": "..."}
  },
  "active_task": {
    "flow_id": "...",
    "step_id": "...",
    "missing_slots": ["..."],
    "filled_slots": {"...": "..."}
  },
  "active_system_task": {
    "flow_id": "...",
    "step_id": "...",
    "slot_name": "..."
  },
  "paused_tasks": [
    {"flow_id": "...", "step_id": "..."}
  ],
  "focused_object": {
    "type": "...",
    "id": "...",
    "title": "..."
  },
  "user_message": "..."
}
```

重点是：

- 去掉了 `runtime_state.last_route.track`
- 厚重的 `last_task_outcome` 被压扁
- `focused_object.attributes` 默认去掉答案型字段
- `active_task / paused_tasks` 只保留状态决策最需要的部分

## 4. 审计现在怎么卡样本

样本进入 SFT 前，必须先过四道门：

1. 语言自然度
2. 时间线一致性
3. 状态-标签一致性
4. 对象-槽位一致性

实现位置：

- [audit_helpers.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/audit_helpers.py)
- [audit_rules.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/audit_rules.py)

导出规则：

- 默认只导出 `audit_meta.passed_for_sft = true` 的样本
- `--allow-unsafe` 才允许把问题样本也导出

## 5. 这轮实际跑出来了什么

数据脚本已跑通：

- [validate_dataset.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/validate_dataset.py)
- [audit_dataset.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/audit_dataset.py)
- [export_sft.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/scripts/export_sft.py)

产物：

- 审计 JSON：[ai_audit.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reports/ai_audit.json)
- 审计 Markdown：[ai_audit.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reports/ai_audit.md)
- 安全导出：`train=374`, `val=69`

关键指标：

- `sft_ready_pass_rate = 0.8358`
- `language_naturalness_pass_rate = 0.8943`
- `history_state_consistency_pass_rate = 0.9340`
- `object_slot_consistency_pass_rate = 0.9925`

## 6. 当前被挡下的主要脏样本来源

当前被审计挡下的样本主要来自四类问题：

1. `ambiguous_all_null` 里还残留模板痕迹
2. `directive_exit_runtime` 和部分 `active_task_slot_fill` 的时间线不完整
3. 少量 `work_order_read_only_task` 的对象类型和用户指代不一致
4. 一小批旧样本还保留显式自我标注

这意味着下一步不是改 schema，而是优先做：

- reduced 数据清单清洗
- 问题样本成组修复
- 同句异状态对照增强

## 7. 对后续训练的直接影响

这次重构之后，下一轮训练前提变成了：

1. 默认只用 `passed_for_sft=true` 的数据
2. 高损失 `read_only` 不再作为统一 SFT 的主学习负担
3. reduced 训练要重点盯：
   - `active_task_slot_fill`
   - `task_interrupt_resume_cancel`
   - `need_clarify / ambiguous_all_null`
4. 如果某条样本逻辑链不自洽，宁可留在问题样本库，也不再硬喂进 SFT

## 8. 当前边界

这次已经完成的是：

- 协议兼容层拆分
- 训练输入白名单收缩
- `semantic_meta / audit_meta` 入链
- 安全导出闭环

这次还没做的是：

- 逐条修完所有 `passed_for_sft=false` 的样本
- 基于新审计门槛重切 reduced 训练集
- 启动下一轮 reduced SFT

所以这份文档是“重构已经落地”的记录，不是“下一轮已经准备完毕”的宣告。
