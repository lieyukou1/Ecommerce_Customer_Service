# Optimize

- 最后修改时间：2026-06-01 20:05:01
- 文档定位：优化阶段导航、方法论入口、history 规范
- 上级入口：[PROJECT_CONTEXT.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/PROJECT_CONTEXT.md)
- 下级入口：[06_第三阶段优化计划.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/06_第三阶段优化计划.md)、[09_新架构候选对比.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/09_新架构候选对比.md)、[10_推荐方案与迁移路线.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/10_推荐方案与迁移路线.md)、[history](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/history)

## 当前阅读顺序

1. [06_第三阶段优化计划.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/06_第三阶段优化计划.md)
2. [08_长对话回归集设计与执行规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/08_长对话回归集设计与执行规范.md)
3. [09_新架构候选对比.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/09_新架构候选对比.md)
4. [10_推荐方案与迁移路线.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/10_推荐方案与迁移路线.md)
5. [TurnPlan 微调工作区 README](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/README.md)
6. [TurnPlan 微调总报告](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/turnplan_finetune_master_report.md)

## 当前阶段结论

- 第三阶段唯一 P0：方案 B - 显式会话状态机重构。
- 旧架构下的局部修补项，不再作为当前主线。
- 状态机采用渐进接管，先稳状态流转，再扩业务智能度。

## 文档职责

- `06_第三阶段优化计划.md`：当前 P0 排期、优先级、执行顺序。
- `08_长对话回归集设计与执行规范.md`：长对话回归集结构、断言、执行方式。
- `09_新架构候选对比.md`：A/B/C 方案对比，解释为什么选 B。
- `10_推荐方案与迁移路线.md`：方案 B 的实施顺序与迁移分批。
- `Material/Finetune/turnplan_qwen3_14b/`：TurnPlan 微调实验工作区，包含稳定文档、原始结果、按轮归档与评测脚本。
- `history/`：每一批优化的历史报告与复盘记录。

## 微调文档迁移说明

TurnPlan 微调相关文档已经整体迁入：

- [Material/Finetune/turnplan_qwen3_14b/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/README.md)
- [Material/Finetune/turnplan_qwen3_14b/docs/turnplan_finetune_master_report.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/turnplan_finetune_master_report.md)

`Optimize/` 只继续承接项目级优化方法论、架构演进与 history，不再混放 TurnPlan 微调实验文档。

## history 规范

- 每完成一批优化，必须新增一份 history 报告。
- 命名统一为：
  `YYYY-MM-DD_HHMM_主题.md`
- 报告固定包含：
  - 本轮目标
  - 为什么现在做
  - 实际改动
  - 回归结果
  - 未完成项
  - 下一步优先级

## 回归绑定规则

- 每批优化后必须执行：
  `precheck -> regression -> browser smoke`
- 产物默认写入：
  `functional-test-workspace/reports/<timestamp>/`
- 这些产物是阶段门禁，不是临时调试副产物。
