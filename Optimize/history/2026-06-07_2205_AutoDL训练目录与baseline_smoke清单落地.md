# 2026-06-07 22:05 AutoDL 训练目录与 baseline/smoke 清单落地

## 本轮目标

- 把当前 AutoDL 4090 机器的落盘约束正式写成训练规范
- 把 TurnPlan 训练前 baseline 执行口径收成一份清单
- 把统一模型替换后的其他轨道 smoke prompts 固化成文档

## 为什么现在做

- 当前云机已经到位，不能再用“理想通用机器”来写执行方案
- 这台机器的主要约束是系统盘小，不提前收好目录和缓存，训练前就可能踩盘满问题
- 前面做数据集时已经暴露出“假多样性”和“机械排列组合”的教训，baseline 与 smoke 不能再沿用那种思路

## 实际改动

1. 新增：
   - [Material/Finetune/turnplan_qwen3_14b/docs/13_AutoDL4090训练目录与落盘规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/13_AutoDL4090训练目录与落盘规范.md)
   - [Material/Finetune/turnplan_qwen3_14b/docs/14_TurnPlan训练前Baseline执行清单.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/14_TurnPlan训练前Baseline执行清单.md)
   - [Material/Finetune/turnplan_qwen3_14b/docs/15_统一模型替换后的其他轨道SmokePrompts.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/15_统一模型替换后的其他轨道SmokePrompts.md)
2. 更新：
   - [Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md)
   - [Optimize/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/README.md)

## 本轮锁定的新口径

- 当前首台训练机按单卡 `RTX 4090 48GB` 主线执行
- 系统盘只放轻资产，重资产统一落数据盘 `/root/autodl-tmp`
- baseline 必须同时保留现网、未训基座、微调候选三套对照
- smoke prompts 明确禁止回到“前缀 + 核心 + 后缀”的排列组合式设计

## 回归结果

- 本轮仅新增与更新文档
- 未执行训练、评测或浏览器 smoke

## 未完成项

- 训练脚本目录和 manifest 生成脚本尚未正式创建
- baseline 的实际运行命令与输出目录还未落成代码
- smoke prompts 还未转成可直接执行的脚本输入

## 下一步优先级

1. 把 `13` 文档里的目录与缓存规范落实到云机实际环境变量和启动脚本
2. 按 `14` 文档顺序先跑现网 baseline 与本地未训基座 baseline
3. 再把 `15` 的 smoke prompts 整理成可复用的对话脚本或评测输入
