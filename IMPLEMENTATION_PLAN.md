# IMPLEMENTATION_PLAN

- 最后修改时间：2026-06-03 00:10
- 文档定位：当前实施主线与近期执行口径
- 上级入口：[PROJECT_CONTEXT.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/PROJECT_CONTEXT.md)
- 下级入口：[SESSION_HANDOFF.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/SESSION_HANDOFF.md)、[Optimize/06_第三阶段优化计划.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/06_%E7%AC%AC%E4%B8%89%E9%98%B6%E6%AE%B5%E4%BC%98%E5%8C%96%E8%AE%A1%E5%88%92.md)

## 当前阶段

- Phase 03：优化与稳定化
- 当前唯一 P0：方案 B，显式会话状态机重构
- 当前执行口径：功能/协议收敛已经过门禁，正在做结构收敛

## 当前硬约束

1. 架构清晰、可解释、模块短小，高于 badcase 命中率
2. 不把关键词硬命中当主判定路径
3. 主判定顺序固定为：LLM 结构化输出 -> 显式上下文/协议 -> 状态机接管
4. 回归集是阶段门禁，不是本轮唯一目标
5. 不默认下潜到 `task/command/processor.py` 和 `task/flow/executor.py`

## 本批正式完成

1. `Planner -> Protocol Gate -> State Decision -> Track Execution` 的主链已经落地
2. `Protocol Gate` 已收口到 [protocol_gate.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/protocol_gate.py)
3. `State Decision` 已收口到 [engine/state_decision](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/engine/state_decision)
4. `Track Execution` 已收口到 [engine/track_execution](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/engine/track_execution)
5. 旧 `engine/runtime`、`engine/turns` 实现已退场
6. `engine` 与 `plan` 当前文件体量满足结构约束

## 当前验证基线

- 编译检查：通过
- 结构红线检查：通过
- 最新正式回归：
  [functional-test-workspace/reports/20260602_154247/report.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/functional-test-workspace/reports/20260602_154247/report.md)
- 当前结果：
  - API：`pass 10 / behavior_fail 1 / infra_fail 0`
  - Browser：本轮跳过
  - Property backend：本轮跳过预检

## 当前判断

- 单点回归不再作为当前批次阻塞项
- 现在的主目标是完成最后一轮架构收尾，而不是继续围绕回归表现纠缠
- 只要完成必要的边界收官，这轮重构就可以收口

## 当前不提级的模块

- [processor.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/task/command/processor.py)
- [executor.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/task/flow/executor.py)

只有满足以下证据之一，才允许把它们提进排期：

1. 上游 plan 已明确正确，但执行结果状态错了
2. slot 已齐，但执行层仍卡住
3. task 切换 / 恢复 / 取消在执行层发生真实语义冲突

## 下一步顺序

1. 清掉旧层残影，让代码树与“6 个一级概念”一致
2. 再收一轮 `state_decision` 的中间协议暴露面
3. 再压一轮 `track_execution` 的公开入口
4. 降低 `focus/` 的架构存在感
5. 完成后转入架构图、总结和面试材料准备
