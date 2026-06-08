# PROJECT_CONTEXT

- 最后修改时间：2026-06-02 09:18:00
- 当前阶段：Phase 03 优化与稳定化
- 当前唯一 P0：方案 B - 显式会话状态机重构

## 构建 / 运行入口

- 工作根目录：`D:\Desktop\SGG_Project\Ecommerce_Customer_Service`
- 后端目录：`D:\Desktop\SGG_Project\Ecommerce_Customer_Service\customer-service-backend`
- 后端启动：
  `D:\Desktop\SGG_Project\Ecommerce_Customer_Service\customer-service-backend\.venv\Scripts\python.exe D:\Desktop\SGG_Project\Ecommerce_Customer_Service\customer-service-backend\atguigu\main.py`
- 前端目录：`D:\Desktop\SGG_Project\Ecommerce_Customer_Service\customer-service-frontend`
- 前端启动：`npm run dev`
- 回归目录：`D:\Desktop\SGG_Project\Ecommerce_Customer_Service\functional-test-workspace`
- 回归命令：
  `npm run precheck`
  `npm run run`
  `npm run run:breakpoint`
- 回归产物目录：`functional-test-workspace/reports/<timestamp>/`
- 常用后端联调地址：`http://127.0.0.1:18082`

## 关键架构约束

- 第三阶段当前主线只有一个：方案 B 状态机重构
- 当前不再以零散补 `if` 作为主要推进方式，局部修补只能服务于状态机渐进接管
- 第一批优先接管：退出、上下文切换、对象承接、任务切换
- 先稳住状态流转可控性和可观测性，再追求更智能的业务效果
- 长对话回归集是固定门禁，不是当前架构优化的唯一目标
- 回归失败先区分：`infra_fail`、`behavior_fail`、`placeholder_pass`
- 每批优化后固定执行：`precheck -> regression -> browser smoke`
- 每批优化后必须补：`Optimize/history/YYYY-MM-DD_HHMM_主题.md`

### 硬规则

- 每个模块只允许一个明确职责，且职责必须能用一句话描述
- `engine` 只负责编排调度，不承担具体业务判断
- 意图识别、状态流转、动作执行必须拆开，不得混写
- 单文件不超过 `450` 行；单函数不超过 `80` 行
- 模块内不允许 `5` 层及以上函数嵌套
- 禁止用关键词列表、词汇集合、`if/elif` 枚举做主意图匹配
- 主判定应优先依赖：
  - LLM 结构化输出
  - 显式上下文决策协议
  - 状态机统一接管
- 重构时发现旧的词汇硬命中逻辑，应替换或降级为最小兜底，不得继续扩张

### 目录规则

- 正式开发主目录固定为：`D:\Desktop\SGG_Project\Ecommerce_Customer_Service`
- 当前正式主战场：`customer-service-backend`
- 当前回归工作区：`functional-test-workspace`
- `备份/` 只作只读回溯参考源，不作为运行目录，不整目录覆盖回正式代码
- `updating/` 和老师参考代码目录也只作参考源，不直接承接正式开发状态
- `functional-test-workspace/reports/` 是回归产物目录，不是协作文档入口
- `Optimize/history/` 只记录每批优化落地结果，不承载临时草稿

## 按任务类型跳转文档

- 当前实施主线与近期执行口径：
  [IMPLEMENTATION_PLAN.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/IMPLEMENTATION_PLAN.md)
- 当前会话状态、阻塞点、下一步：
  [SESSION_HANDOFF.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/SESSION_HANDOFF.md)
- 第三阶段 P0 排期与执行口径：
  [Optimize/06_第三阶段优化计划.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/06_%E7%AC%AC%E4%B8%89%E9%98%B6%E6%AE%B5%E4%BC%98%E5%8C%96%E8%AE%A1%E5%88%92.md)
- 长对话回归集设计与断言规范：
  [Optimize/08_长对话回归集设计与执行规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/08_%E9%95%BF%E5%AF%B9%E8%AF%9D%E5%9B%9E%E5%BD%92%E9%9B%86%E8%AE%BE%E8%AE%A1%E4%B8%8E%E6%89%A7%E8%A1%8C%E8%A7%84%E8%8C%83.md)
- 新架构候选与迁移路线：
  [Optimize/09_新架构候选对比.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/09_%E6%96%B0%E6%9E%B6%E6%9E%84%E5%80%99%E9%80%89%E5%AF%B9%E6%AF%94.md)
  [Optimize/10_推荐方案与迁移路线.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/10_%E6%8E%A8%E8%8D%90%E6%96%B9%E6%A1%88%E4%B8%8E%E8%BF%81%E7%A7%BB%E8%B7%AF%E7%BA%BF.md)
- 优化方法论与历史记录：
  [Optimize/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/README.md)
  [Optimize/history](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/history)
- 参考资料与验收导航：
  [Material/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/README.md)
  [Evaluation/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Evaluation/README.md)
- 直接运行回归、查看 artifacts：
  [functional-test-workspace/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/functional-test-workspace/README.md)
