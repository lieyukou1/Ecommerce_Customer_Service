# round_02 Next Round Plan

## 当前状态

本文件原本是“直接开 `round_03`”的预案，但在同口径基座诊断完成后，当前状态已经改成:

- **暂停直接开 `round_03`**
- **先完成方案级重定义**

## 已锁定的新方向

### 1. 不再整体硬学 read-only 边界

统一 `TurnPlan` 主任务不再继续把所有 `read-only task vs knowledge` 都当成同一类学习问题。

新的口径是:

- `read-only` 不整体拆掉
- 只拆高业务损失部分
- 低损失规则 / 说明类只读继续保留

### 2. 先救高损失场景

高损失集合固定为:

- `resident_work_orders_list_query`
- `resident_service_items_list_query`
- `work_order_status_query`
- `service_progress_tracking`
- `service_item_detail_query`

短期先在 runtime 归一化层吸收这部分边界，优先保证业务结果，而不是继续让模型纯靠 SFT 去背这条内部通道约定。

### 3. 统一主任务收缩

如果后续真的开 `round_03`，统一 `TurnPlan` 主任务收缩为:

- 办理类意图识别
- 业务槽位抽取
- 多轮任务状态管理
- 中断 / 恢复 / 取消 / 退出
- 模糊表达 -> `clarify`
- `chitchat / directive / all_null`

## 下一阶段先做什么

1. 写清新的任务定义与边界说明
2. 重写主训练集 / 单独评测集口径
3. 先用未训练 `Qwen3-14B` 跑新口径 baseline
4. 判断基座在“新主任务”上是否已经足够强
5. 只有仍存在明确增益空间时，才启动 reduced `round_03`

## 下一阶段不做什么

- 不直接开新训练
- 不继续沿用“统一任务不变，只补少量 read-only 对照样本”的路线
- 不把 `top_level_track_accuracy` 继续当作唯一主指标
- 不把 `read-only` 一刀切整体从项目能力口径里删除

## 新的重点观察指标

主看:

1. `task_command_family_accuracy`
2. 业务类 bucket accuracy
3. `slot_fill_exact_match`
4. `protocol_gate_pass_rate`
5. `high_loss_read_only_metrics.system_success_rate`

辅助看:

- `knowledge_false_positive_rate`
- `adjusted_protocol_gate_pass_rate`
- 高损失 `read-only` 的分项成功率

## 当前文档入口

- [17_Round03前置重定义方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/17_Round03前置重定义方案.md)
- [18_高损失ReadOnly与Round03评测口径.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/18_高损失ReadOnly与Round03评测口径.md)

## 回退条件

如果后续验证发现下面任一情况成立，则继续暂停 `round_03`:

- 高损失 `read-only` 仍主要靠模型硬学边界才能成功
- 基座在新口径主任务上已经足够强，SFT 增益空间不明显
- runtime 吸收逻辑引入新的系统性副作用
