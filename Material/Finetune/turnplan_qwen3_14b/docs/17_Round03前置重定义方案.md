# Round_03 前置重定义方案

- 最后修改时间: 2026-06-07
- 定位: 在 `round_03` 真正开训之前，先重定义任务边界、主训练目标和评测口径
- 上级入口: [turnplan_finetune_master_report.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/turnplan_finetune_master_report.md)

## 1. 当前结论

连续两轮统一 `TurnPlan` SFT 都没有稳定压过未训练 `Qwen3-14B` 基座，当前不再直接进入 `round_03` 训练。

这一轮先做 4 件事:

1. 重定义 `read-only` 边界
2. 收缩统一 `TurnPlan` 主任务
3. 重写主训练集与单独评测集口径
4. 先跑未训练基座的新口径 baseline，再决定要不要开新训练

## 2. read-only 边界重定义

### 2.1 只拆高业务损失部分

以下 flow 从统一 `TurnPlan` 主任务里剥离，不再要求模型单纯靠 SFT 死记边界:

- `resident_work_orders_list_query`
- `resident_service_items_list_query`
- `work_order_status_query`
- `service_progress_tracking`
- `service_item_detail_query`

原因不是“这几类更像 task”，而是:

- 一旦误落 `knowledge` 或 `all_null`
- 当前 runtime 会少掉对象卡片、实时 action 或结构化只读查询结果
- 这会造成真实业务损失，而不只是协议纯度下降

### 2.2 低损失只读仍保留

以下内容暂不从统一主任务中整体移出:

- 规则类知识问答
- 低风险对象追问
- 低风险说明类 follow-up

这些场景即使落到 `knowledge`，大多数情况下仍能回答，不值得继续把训练预算大量消耗在“内部通道纯度”上。

### 2.3 短期落地层

短期改动优先放在:

- [turn_plan_normalizer.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/turn_plan_normalizer.py)

目标是:

- 优先吸收高损失 `read-only`
- 尽量不大拆执行层
- 先验证方向，再决定是否把长期架构正式升级成“语义统一、执行分流”

## 3. 统一 TurnPlan 主任务的新定义

`round_03` 的统一 `TurnPlan` 主任务收缩为:

- 办理类意图识别
- 业务槽位抽取
- 多轮任务状态管理
- 中断 / 恢复 / 取消 / 退出
- 模糊表达 -> `clarify` 触发
- `chitchat / directive / all_null` 区分

对应老师能力口径时，当前主张如下:

### 3.1 重点保留

- `4.3.1` 用户意图识别能力:
  - 重点保留办理类、多轮切换类、模糊澄清类
- `4.3.2` 槽位抽取能力:
  - 重点保留核心业务槽位
- `4.3.3` 多轮流程状态管理能力:
  - 作为当前最值得打的主项

### 3.2 明确降级表述

- `4.3.4` 澄清问题生成能力:
  - 当前只覆盖“是否进入 clarify”
  - 不宣称澄清话术本身已被专项微调
- `4.3.5` 异常处理与人工升级能力:
  - 当前仍是弱覆盖
  - 不包装成本轮微调的强项

## 4. Round_03 的推进顺序

固定顺序如下:

1. 写清新的任务定义与边界说明
2. 重写主训练集 / 单独评测集口径
3. 用未训练 `Qwen3-14B` 跑新口径 baseline
4. 判断基座在新主任务上是否已经足够强
5. 只有仍存在明确增益空间时，才启动 reduced `round_03`

## 5. 这一轮不做什么

- 不直接开新训练
- 不把所有 `read-only` 一刀切整体拆掉
- 不继续沿用“统一任务不变，只补几条 read-only 对照样本”的思路
- 不把 `top_level_track_accuracy` 当作下一轮唯一主指标

## 6. 当前实现落点

当前代码层已开始落实的部分:

- 高损失 `read-only` 的短期吸收逻辑进入
  - [turn_plan_normalizer.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/turn_plan_normalizer.py)
- runtime 评测脚本新增高损失 `read-only` 的业务成功率出口
  - [eval_turnplan_runtime.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/eval_turnplan_runtime.py)

更细的评测与数据口径见:

- [18_高损失ReadOnly与Round03评测口径.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/18_高损失ReadOnly与Round03评测口径.md)
