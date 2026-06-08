# Datasets

- 最后修改时间：2026-06-06 17:00
- 文档定位：微调数据集与标注资产入口
- 上级入口：[PROJECT_CONTEXT.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/PROJECT_CONTEXT.md)
- 下级入口：[turnplan-phase1/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/README.md)

## 当前可用数据集

1. [turnplan-phase1/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/README.md)
   - 物业客服 TurnPlan 微调 Phase 1 数据集
   - 任务范围：`task / knowledge / chitchat / directive / all-null`
   - 产物包含 canonical 标注、SFT 导出、schema、校验脚本、离线评测口径

## 与训练实施联动的文档

1. [Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md)
   - 当前物业客服项目的模型选型、训练、评测、部署、回滚、迁移口径
2. [Material/Finetune/turnplan_qwen3_14b/docs/12_通用微调项目全流程指南.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/12_通用微调项目全流程指南.md)
   - 可复用到其他微调项目的通用操作手册

## 使用边界

- 这里放的是“训练与标注资产”，不是线上运行链路代码。
- 数据集的协议来源以
  [turn_plan.jinja2](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/prompt/jinja2/turn_plan.jinja2)
  为准。
- 长对话场景来源优先参考
  [api-scenarios.js](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/functional-test-workspace/scenarios/api-scenarios.js)。
- 运行时字段白名单优先参考
  [03_项目状态流转复习表.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/代码阅读/03_项目状态流转复习表.md)。
