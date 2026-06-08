# reduced_round03 Targeted Repair List

## 用途

这份清单只记录 **下一轮数据修复最值得优先处理的样本形态**。  
它不是完整错误全集，而是为了下一版 reduced 数据集更快下手。

## 已锁定的主问题

1. `active_task_slot_fill` 在 train / val 都掉了
2. `task_interrupt_resume_cancel` 没有稳定受益
3. `ambiguous_all_null` 已明显提升，暂时不继续扩量

## 需要重点补强的具体样本

### 1. active context 下，用户只补短句

#### `tp_active_task_slot_fill_val_006`

- gold:
  - `task.set_slots(rule_topic="社区公约")`
- candidate:
  - `all_null`
- 说明:
  - 已有 `active_task=resident_rule_qa`
  - 已有 `active_system_task=system_collect_information`
  - 用户短句 `社区公约这块` 应该被识别为补槽，不是模糊表达

#### `tp_active_task_slot_fill_val_007`

- gold:
  - `task.set_slots(service_item_id="SVC2008")`
- candidate:
  - `all_null`
- 说明:
  - 已有服务项目详情查询上下文
  - `查一下可视对讲检修详情` 在当前上下文里是补当前槽位，不是重新开题

#### `tp_active_task_slot_fill_val_000`

- gold:
  - `task.set_slots(service_item_id="SVC2001")`
- candidate:
  - `knowledge.service_item_info`
- 说明:
  - 句子本身很像知识咨询
  - 但在当前 active context 下，应优先读成补当前槽位

### 2. 从催办切投诉时，不该掉回 all_null

#### `tp_task_interrupt_resume_cancel_val_006`

- gold:
  - `start_flow(complaint_request_submission)`
  - `set_slots(work_order_id, complaint_reason)`
- candidate:
  - `all_null`
- 说明:
  - 用户说的是自然切换，不是退出
  - 这类样本要继续补“有 active flow 的切换投诉”

### 3. 投诉场景不要被过度保守吞掉

#### `tp_work_order_business_complaint_val_004`

- gold:
  - `start_flow(complaint_request_submission)`
  - `set_slots(work_order_id, complaint_reason)`
- candidate:
  - `all_null`
- 说明:
  - 用户表达里有情绪，也有明确业务升级意图
  - 需要补更多“反复没解决 -> 投诉”的自然句式

## 下一轮补样规则

### active_task_slot_fill

- 必带 active context
- 用户只说自然短句，不自我标注
- gold 以 `set_slots` 为主
- 同一语义做两类对照:
  - 有 active context -> `task.set_slots`
  - 无 active context -> `knowledge` 或 `all_null`

### task_interrupt_resume_cancel

- 同一对象下补三组对照:
  - 取消 flow
  - 退出当前话题
  - 从当前 flow 切投诉

### complaint / urge

- 优先补“情况描述型”自然句子
- 少用显式动作词
- 保持 focused_object 存在，让模型学会借上下文落业务
