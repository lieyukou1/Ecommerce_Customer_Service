# 高损失 Read-Only 与 Round_03 评测口径

- 最后修改时间: 2026-06-07
- 定位: 说明 `round_03` 之前主训练集怎么收缩、单独评测集怎么看、指标如何换挡
- 上级入口: [17_Round03前置重定义方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/17_Round03前置重定义方案.md)

## 1. 主训练集新口径

统一 `TurnPlan` 主训练集去掉高损失 `read-only` 的主学习负担，继续保留并强化:

- `work_order_business_urge`
- `work_order_business_complaint`
- `active_task_slot_fill`
- `task_interrupt_resume_cancel`
- `directive_exit_runtime`
- `ambiguous_all_null`
- `chitchat`
- `object_context_followup` 中的业务继续类样本
- 低损失规则 / 知识类样本

对高损失 `read-only` 的处理方式改成:

- 不再把它当成统一 `TurnPlan` 主任务里最主要的学习矛盾
- runtime 先负责兜住业务正确性
- 再看是否值得把其中一部分提级成专项微调任务

## 2. 单独评测集新口径

新增一套“高损失 read-only system eval”，重点不是看它被判成 `task` 还是 `knowledge`，而是看业务后果。

高损失集合固定为:

- `resident_work_orders_list_query`
- `resident_service_items_list_query`
- `work_order_status_query`
- `service_progress_tracking`
- `service_item_detail_query`

### 2.1 重点观察

- 是否返回对象卡片
- 是否命中实时查询 action
- 是否补齐必要对象 / ID
- 是否保留后续继续追问该对象的上下文能力

### 2.2 当前脚本里的代理指标

当前 [eval_turnplan_runtime.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/eval_turnplan_runtime.py) 已先加一版代理指标，输出:

- `high_loss_read_only_metrics.count`
- `high_loss_read_only_metrics.system_success_rate`
- `high_loss_read_only_metrics.list_query_success_rate`
- `high_loss_read_only_metrics.work_order_runtime_success_rate`
- `high_loss_read_only_metrics.service_item_detail_success_rate`

这版还不是完整“执行后消息级 system eval”，但已经从“纯 track 对齐”前进到了“业务是否真正被救回来”。

## 3. 主指标调整

下一轮不再由 `top_level_track_accuracy` 单独主导结论。

主看:

- `task_command_family_accuracy`
- 业务类 bucket accuracy
- `slot_fill_exact_match`
- `protocol_gate_pass_rate`
- `high_loss_read_only_metrics.system_success_rate`

辅助看:

- `knowledge_false_positive_rate`
- `json_valid_rate`
- `adjusted_protocol_gate_pass_rate`

## 4. Base-Only Replay 的验收口径

在真正进入 `round_03` 训练设计前，先跑未训练 `Qwen3-14B` 的新口径 baseline。

这一步要回答 3 个问题:

1. 在剥离高损失 `read-only` 后，基座在剩余主任务上的表现是否已经足够强
2. normalizer 吸收逻辑是否确实把高损失只读从“协议错”变成了“业务可用”
3. 还有哪些残余问题仍然值得用 SFT 去解决

## 5. 现阶段的晋级条件

只有同时满足下面两点，才进入 reduced `round_03`:

- 新主任务定义稳定
- base-only replay 的结果可解释，且仍存在明确可争取的增益空间

以下情况直接暂停开训:

- 高损失 `read-only` 仍主要靠“模型学边界”才能成功
- 新口径下基座已经足够强，SFT 增益空间过小
- runtime 吸收逻辑引入了新的系统性副作用
