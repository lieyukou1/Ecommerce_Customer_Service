# 历史对话接入规范（Phase 2 预留）

- 最后修改时间：2026-06-06 17:00
- 文档定位：真实历史对话接入 TurnPlan 数据集的预留规范
- 上级入口：[turnplan-phase1/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/README.md)
- 下级入口：无

## 1. 接入目标

Phase 2 才接真实历史对话，但必须落到与 Phase 1 完全相同的 canonical 结构。

来源预设：

- `dialogue_states.state_json -> sessions -> turns`

## 2. 只收哪些历史样本

优先收录：

- 4+ 轮长对话
- 存在对象切换
- 存在任务切换
- 存在退出 / 重开
- 存在 active task 补槽
- 存在知识 -> 任务 / 任务 -> 知识切换

不收：

- 纯寒暄噪声
- 编码异常文本
- 没有标注价值的重复追问
- 只靠 1-2 轮即可判断的“好看样本”

## 3. 清洗规则

- 保留真正导致状态串味或成功收口的上下文链
- 删除无意义口头禅、页面提示残片、重复系统确认
- 把对象上下文、active task、last route 等关键信息提取成 canonical 输入字段

## 4. 标注要求

- `source` 必须标为 `history-backed`
- 仍然遵守 Phase 1 的单轨 / 全 null 约束
- 如果历史场景与现有标注规则冲突，先回到
  [annotation-spec.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/docs/annotation-spec.md)
  修规则，再决定是否入库

## 5. 接入顺序

建议 Phase 2 先接以下 4 类：

1. 工单只读追问切业务办理
2. 服务项目说明追问后退出
3. active task 补槽期间切换意图
4. 多对象切换后重新聚焦
