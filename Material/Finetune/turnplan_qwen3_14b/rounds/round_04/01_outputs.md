# round_04 Outputs

- 轮次入口: [00_run_manifest.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/00_run_manifest.md)
- 报告索引: [report_index.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/rounds/round_04/artifacts/report_index.md)

## 代码产出

- `TurnPlanNormalizer` 已收缩为编排层，只保留退出归一化和 resolver 调度
- 高损失 `read_only` 兼容逻辑已下沉到 [read_only_resolver.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/read_only_resolver.py)
- 联合审计、输入清洗、安全导出链路已落地
- 新增 reduced round_04 数据脚本：
  - [reduced_round04_dataset_utils.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/reduced_round04_dataset_utils.py)
  - [repair_reduced_round04_active_task_slot_fill.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/repair_reduced_round04_active_task_slot_fill.py)
  - [rebuild_reduced_round04_ambiguous_all_null.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/rebuild_reduced_round04_ambiguous_all_null.py)
  - [rebuild_reduced_round04_directive_exit_runtime.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/rebuild_reduced_round04_directive_exit_runtime.py)
  - [assemble_reduced_round04_candidate.py](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/scripts/assemble_reduced_round04_candidate.py)

## canonical 审计结果

- canonical 记录数：
  - `train = 450`
  - `val = 80`
- safe SFT 导出数：
  - `train = 374`
  - `val = 69`
- 审计主指标：
  - `sft_ready_pass_rate = 0.8358`
  - `language_naturalness_pass_rate = 0.8943`
  - `history_state_consistency_pass_rate = 0.9340`
  - `object_slot_consistency_pass_rate = 0.9925`

## reduced round_04 切分结果

- [reduced_round04_triage_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_triage_v1/summary.md)
- [reduced_round04_keep_base_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_keep_base_v1/summary.md)
- `keep_total = 122`
- `targeted_fix_total = 60`
- `bucket_rebuild_total = 82`

## repaired / rebuilt 产物

- [reduced_round04_active_task_slot_fill_repair_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_active_task_slot_fill_repair_v1/summary.md)
- [reduced_round04_ambiguous_all_null_rebuild_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_ambiguous_all_null_rebuild_v1/summary.md)
- [reduced_round04_directive_exit_runtime_rebuild_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_directive_exit_runtime_rebuild_v1/summary.md)

## reduced round_04 candidate 结果

- [reduced_round04_candidate_v1/summary.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_candidate_v1/summary.md)
- [reduced_round04_candidate_v1/manifest.json](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_candidate_v1/manifest.json)
- [reduced_round04_candidate_v1_exports_llm/sft_train.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_candidate_v1_exports_llm/sft_train.jsonl)
- [reduced_round04_candidate_v1_exports_llm/sft_val.jsonl](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/reduced_round04_candidate_v1_exports_llm/sft_val.jsonl)

口径固定：

- `reduced_round04_candidate_v1` 是 **验证型训练集**
- 它的用途是验证“当前重定义后的 unified Planner SFT 方向是否成立”
- 它**不是**最终生产微调集
- 若方向成立，下一步目标是扩成 `production-oriented expansion set`

本轮 candidate 统计：

- total: `264`
- train: `225`
- val: `39`
- `sft_ready_records = 264`
- `unsafe_records = 0`
- `duplicate_pairs = 0`
- `unique_user_messages = 220`

bucket 分布：

- `active_task_slot_fill = 60`
- `ambiguous_all_null = 41`
- `directive_exit_runtime = 41`
- `task_interrupt_resume_cancel = 52`
- `work_order_business_complaint = 35`
- `work_order_business_urge = 35`

上下文分布：

- `active_task_records = 133`
- `active_system_task_records = 66`
- `paused_task_records = 22`
- `history_length_distribution = {0:29, 2:100, 3:27, 4:75, 6:33}`

## 最小运行验证

已验证：

- 当 `focused_object=work_order`
- Planner 原始输出为 `knowledge.intents=["work_order_info"]`
- 用户是在问只读状态 / 进度

[TurnPlanNormalizer.normalize(...)](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/customer-service-backend/atguigu/plan/turn_plan_normalizer.py) 可稳定改写为只读 `task`：

- `start_flow(service_progress_tracking | work_order_status_query)`
- `set_slots(work_order_id=focused_object.id)`
