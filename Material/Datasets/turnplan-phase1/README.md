# TurnPlan Phase 1

- 最后修改时间：2026-06-06 16:35
- 文档定位：物业客服 TurnPlan 微调数据集 Phase 1 入口
- 上级入口：[Material/Datasets/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/README.md)
- 下级入口：
  - [docs/annotation-spec.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/docs/annotation-spec.md)
  - [docs/offline-evaluation.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/docs/offline-evaluation.md)
  - [docs/history-backed-phase2-spec.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/docs/history-backed-phase2-spec.md)
- 协同文档：
  - [Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md)
  - [Material/Finetune/turnplan_qwen3_14b/docs/12_通用微调项目全流程指南.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/12_通用微调项目全流程指南.md)

## 这一批数据集做什么

- 只做 `TurnPlan` 生成微调，不做最终客服回复微调。
- 输出目标固定为标准 `TurnPlan JSON`，顶层只允许：
  - `task`
  - `knowledge`
  - `chitchat`
  - `directive`
- 允许四字段全 `null`，用于“方向仍不明确，需要继续澄清”的样本。

## 当前产物

- `canonical/records_train.jsonl`
- `canonical/records_val.jsonl`
- `exports/sft_train.jsonl`
- `exports/sft_val.jsonl`
- `reports/ai_audit.json`
- `reports/ai_audit.md`
- `scripts/build_dataset.py`
- `scripts/validate_dataset.py`
- `scripts/export_sft.py`
- `scripts/audit_dataset.py`
- `scripts/extract_history_backed.py`

## 当前规模

| Bucket | Train | Val |
| --- | ---: | ---: |
| chitchat | 40 | 8 |
| directive_exit_runtime | 35 | 6 |
| ambiguous_all_null | 35 | 6 |
| service_item_knowledge | 55 | 10 |
| work_order_read_only_task | 85 | 16 |
| work_order_business_urge | 30 | 5 |
| work_order_business_complaint | 30 | 5 |
| active_task_slot_fill | 50 | 10 |
| object_context_followup | 45 | 7 |
| task_interrupt_resume_cancel | 45 | 7 |

总计：
- 训练集：450
- 验证集：80

## AI 审计结果（当前基线）

- 全量样本：530
- 全量唯一 `input + label` 对：530
- 精确重复对：0
- 唯一 `user_message`：511
- 唯一 `history`：109
- Flow 白名单覆盖：8 / 8
- Knowledge intent 白名单覆盖：8 / 8
- `contact_phone` 槽位记录：23
- `complaint_confirm` 否定样本：15
- `active_system_task` 合同说明：已显式写入训练 system prompt
- `knowledge.intents` 数组合同：已显式写入训练 system prompt
- `start_flow / resume_flow` 的 `flow` 字段合同：已显式写入训练 system prompt

当前 flow 分布已经做过一轮均衡化：
- query 类 flow：16-18 条 / flow
- `work_order_urge_submission`：61
- `complaint_request_submission`：48

详细审计见：
- [reports/ai_audit.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reports/ai_audit.json)
- [reports/ai_audit.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reports/ai_audit.md)

## 数据来源口径

Phase 1 只使用仓库内素材：
1. [turn_plan.jinja2](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/prompt/jinja2/turn_plan.jinja2)
   - 作为协议与标注规范源
2. [api-scenarios.js](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/functional-test-workspace/scenarios/api-scenarios.js)
   - 作为长对话高价值场景源
3. [03_项目状态流转复习表.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Docs/代码阅读/03_项目状态流转复习表.md)
   - 作为训练输入字段白名单源

## 历史对话抽取能力

- 已保留 `history-backed` 接入能力，不需要重做脚本。
- 抽取脚本：`scripts/extract_history_backed.py`
- 支持两条入口：
  - `--from-db`：从 `dialogue_states.state_json -> sessions -> turns` 抽取
  - `--input-jsonl`：从人工整理后的 JSONL 二次转换
- 当前推进口径：
  - 先通过 AI 审计
  - 再做人工抽检
  - 再做真实手动对话
  - 最后才进入历史对话抽取与整理

## 命令

在仓库根目录执行：

```powershell
python Material\Datasets\turnplan-phase1\scripts\build_dataset.py
python Material\Datasets\turnplan-phase1\scripts\validate_dataset.py
python Material\Datasets\turnplan-phase1\scripts\export_sft.py
python Material\Datasets\turnplan-phase1\scripts\audit_dataset.py
```

如果要用外部 LLM 把语言层整体重写成更自然的口语数据：

```powershell
$env:TURNPLAN_LLM_API_KEY="你的 key"
$env:TURNPLAN_LLM_BASE_URL="https://jsyai.xinglian.work"
python Material\Datasets\turnplan-phase1\scripts\llm_rewrite_dataset.py --split both --output-dir Material\Datasets\turnplan-phase1\canonical_llm
python Material\Datasets\turnplan-phase1\scripts\validate_dataset.py --input-dir Material\Datasets\turnplan-phase1\canonical_llm
python Material\Datasets\turnplan-phase1\scripts\audit_dataset.py --input-dir Material\Datasets\turnplan-phase1\canonical_llm --report-dir Material\Datasets\turnplan-phase1\reports_llm
python Material\Datasets\turnplan-phase1\scripts\export_sft.py --input-dir Material\Datasets\turnplan-phase1\canonical_llm --output-dir Material\Datasets\turnplan-phase1\exports_llm
```

说明：
- `llm_rewrite_dataset.py` 会自动组装多模型池：
  - 你提供的网关：默认模型 `gpt-5.4-mini`
  - 项目现有 `customer-service-backend/.env` 里的 DeepSeek：当前是 `deepseek-v4-flash`
- 脚本会先做模型探活，只使用当前可用的模型
- 每条样本会按稳定路由选择重写模型，并尽量由另一模型做交叉复核
- 如果某个模型临时不可用，脚本会自动回退，不会整批直接崩掉

## 当前阶段门禁

- `build_dataset.py` 必须通过：不允许精确重复 input+label 对
- `validate_dataset.py` 必须通过：不允许 coverage / contract / diversity 回退
- `validate_dataset.py` 额外检查：
  - `contact_phone` 槽位覆盖
  - `complaint_confirm` 否定样本覆盖
- `audit_dataset.py` 必须生成最新报告：作为人工抽检前的 AI 评估结果
- 人工抽检通过后，再进入真实对话采样与 `history-backed` 数据整理
