# Functional Test Workspace

- 最后修改时间：2026-06-02 08:00:00
- 文档定位：长对话回归与浏览器烟测工作区说明
- 上级入口：[Optimize/08_长对话回归集设计与执行规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/08_长对话回归集设计与执行规范.md)
- 下级入口：[reports](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/functional-test-workspace/reports)

## 用途

- 环境预检查
- 长对话 API 回归
- 浏览器烟测
- 正式 run artifacts 输出

## 运行入口

- `npm run precheck`
- `npm run run`
- `npm run run:breakpoint`

## 固定执行顺序

1. `precheck`
2. `long-dialogue regression`
3. `browser smoke`
4. artifact generation

## 日志与产物

每次正式运行固定写入：

- `reports/<timestamp>/run.json`
- `reports/<timestamp>/report.md`
- `reports/<timestamp>/regression-baseline.md`
- `reports/<timestamp>/` 下的浏览器截图

这些产物是阶段门禁记录，不是临时调试副产物。

## 当前断言重点

- 三轨切换
- 对象切换
- 任务切换
- 退出与再进入
- 每轮状态字段与关键话术校验
- 区分两类 task 收口：
  - 即时完成型 task（`completed_with_focus`）
  - 挂起等待补槽位的 task（`waiting_for_slot`）

## 当前补充断言能力

- `expected_task_outcome_kind`
- `expected_task_outcome_kinds`
- `expected_task_outcome_flow_id`
- `task_outcome_reason_includes`

这些字段用于表达“这一轮进了 task，但是否应该挂住”。

## 依赖说明

- 深状态验证依赖后端测试态 state snapshot API。
- 前端烟测负责用户可见行为，深状态断言留在 API 回归侧。
