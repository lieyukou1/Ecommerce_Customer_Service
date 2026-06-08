# TurnPlan 微调实施方案

- 最后修改时间：2026-06-07
- 文档定位：物业智能管家项目的 TurnPlan 微调、评测、部署、回滚、迁移执行方案
- 上级入口：[../README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/README.md)
- 协同入口：
  - [Material/Datasets/turnplan-phase1/README.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/README.md)
  - [Material/Datasets/turnplan-phase1/docs/offline-evaluation.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Datasets/turnplan-phase1/docs/offline-evaluation.md)
  - [Optimize/04_7B模型部署清单与云服务器技术手册.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Optimize/04_7B模型部署清单与云服务器技术手册.md)

## 1. 本轮目标

本轮只做一件事：把当前项目里最适合微调的子任务先做成一个可上线、可回滚、可迁移的闭环。

这件事具体是：

- 只训练 `TurnPlan` 生成
- 用训练结果提升 `Planner` 的结构化决策稳定性
- 最终上线时，把**整个项目的 LLM** 统一切到同一个本地 14B 模型
- 但评测时，`Planner` 和其他表达轨道必须分层验收

这里要特别区分两个口径：

1. 训练目标只覆盖 `TurnPlan`
2. 最终部署替换范围是全项目 LLM

这不是矛盾，而是为了同时满足两件事：

- 微调要聚焦一个清晰子任务，避免目标发散
- 上线后要用统一模型承接项目里所有 LLM 调用，避免维护两套能力栈

## 2. 为什么先做 TurnPlan

当前项目里，LLM 的角色可以分成两类：

1. **结构化决策**
   - 代表模块：`TurnPlanner`
   - 输入：用户消息、历史、focused object、active task、runtime state
   - 输出：结构化 `TurnPlan JSON`
2. **自然语言表达**
   - 代表模块：`clarify / knowledge / chitchat`
   - 输入：系统已经做出的判断与上下文
   - 输出：给用户看的中文回复

TurnPlan 是最适合先微调的原因有四个：

- 标签空间小，输出协议固定
- 好坏容易看，不需要猜模型“是不是懂了”
- 可以直接接现有 `protocol gate -> state decision -> replay` 回放链路
- 训练成果能明显落到项目核心主链，而不是只提升措辞漂亮程度

本轮明确不做：

- 最终客服文本微调
- 多轨道同时微调
- 执行层行为改造
- RAG 重构
- 知识库重做

## 3. 基座模型与训练方式

### 3.1 模型选型

本轮主线固定为：

- 基座模型：`Qwen/Qwen3-14B`
- 训练方式：`QLoRA`
- 推理框架：`vLLM`
- 训练框架：`LLaMA-Factory`

选择这条组合的原因：

- 14B 对中文结构化任务和一般表达层都够用
- QLoRA 对单机资源更友好，风险和成本都更可控
- 你当前后端本来就是 OpenAI-compatible 接法，`vLLM` 最顺
- `LLaMA-Factory` 已经能覆盖 LoRA / QLoRA / 导出 / 常见训练参数，不需要自造整套训练底座

### 3.2 为什么不是更小或更大

- 7B：能做，但在多轮上下文、对象切换、模糊表达下更容易抖
- 14B：是当前项目“效果、成本、可用性”的平衡点
- 32B 及以上：效果可能更稳，但单机轮转、国内受限、卡位不稳定的现实下，成本和迁移负担会明显变重

### 3.3 训练方式固定口径

本轮默认配置：

- 量化：4-bit NF4
- 计算精度：bf16
- 适配器：LoRA
- 不做全量微调
- 不做 DPO / PPO / RLHF
- 不做继续在坏 checkpoint 上补训

原因很直接：

- 本轮先求“可控的结构化提升”
- 不是追求把模型整个人格和语言风格都重塑

## 4. 资源与环境

### 4.1 主线资源

本轮推荐主线配置：

- `1 x 48GB GPU`
- `16 vCPU`
- `64GB RAM`
- `200GB NVMe`
- `Ubuntu 22.04`
- `Docker`
- `NVIDIA Container Toolkit`

当前已确认的首台训练机就是 AutoDL 单机：

- `RTX 4090 48GB`
- `25 vCPU`
- `92GB RAM`
- 系统盘 `30GB`
- 数据盘 `/root/autodl-tmp` `223GB`

这意味着训练主线可以直接按单卡 48GB 执行，但必须额外遵守：

- 大模型、缓存、产物优先写入数据盘
- 系统盘不承担训练重资产
- 长任务必须用 `screen` 或同类工具托管

### 4.2 为什么是这个规格

这套规格的目标不是“豪华”，而是：

- 训练能跑通
- 导出能落盘
- 评测能同时执行
- 迁移时不至于反复卡在磁盘或内存上

这份规格已经避免了虚胖：

- 不写 `128GB RAM`
- 不写 `500GB NVMe`
- 不要求两套 14B 模型长期同机常驻

### 4.3 备用资源

如果拿不到 48GB 单卡，再准备：

- `2 x 24GB GPU`

但这只是备用路线，不作为主线写入执行顺序。原因是：

- 单机轮转时，主线越统一越好
- 双卡环境更容易把问题复杂化成通信、切卡、容器、驱动问题

## 5. 当前项目里的训练边界

### 5.1 训练输入

直接复用当前 `turnplan-phase1` 的 canonical / export 资产，训练输入保留这些字段：

- `history`
- `runtime_state.conversation_state`
- `runtime_state.last_route`
- `runtime_state.last_task_outcome`
- `active_task`
- `active_system_task`
- `paused_tasks`
- `focused_object`
- `user_message`

### 5.2 训练输出

输出固定为标准 `TurnPlan JSON`：

- `task`
- `knowledge`
- `chitchat`
- `directive`

一次只能有一个主轨道非空；方向不明时四个字段全 `null`。

### 5.3 不纳入训练的部分

本轮明确不进入训练的数据：

- 最终客服回复文本
- 对象消息原始 click 事件
- 全量 `DialogueState` 快照
- 长期历史 session 归档
- `knowledge / clarify / chitchat` 的专项标注集

## 6. 训练流程

### 6.1 基线阶段

训练前必须保留三套基线：

1. 当前远程现网模型
2. 本地未微调 `Qwen3-14B`
3. 微调候选模型

这三套基线缺一不可：

- 远程现网模型：回答“现在产品实际表现如何”
- 本地未微调模型：回答“是不是底座本身就够了”
- 微调候选：回答“这次数据和训练到底带来了什么”

### 6.2 Pilot Run

先做一轮小规模试跑，只验证链路，不追结果：

- 数据子集：约 15% - 20%
- 单 seed
- 短 epoch
- 目的：
  - 显存是否稳定
  - 日志是否齐全
  - 导出是否正常
  - 评测脚本是否能接上
  - artifact 是否能完整上传

Pilot run 通过后，才能进入 main run。

### 6.3 Main Run

主训练固定做两轮独立 run：

- `seed=42`
- `seed=3407`

默认参数起点：

- `max_seq_len=2048`
- `per_device_train_batch_size=1`
- `gradient_accumulation_steps=16`
- `learning_rate=1e-4`
- `lora_rank=32`
- `lora_alpha=64`
- `lora_dropout=0.05`
- `num_train_epochs=3`
- `warmup_ratio=0.03`
- `eval_steps=50`
- `save_steps=50`
- `early_stopping_patience=2`

这一版不追求把参数卷到极致，而是先把“稳定复现”作为第一优先级。

## 7. 产物与版本管理

### 7.1 每次 run 必须固化的产物

每次训练都必须保留六类真相：

1. 基座模型 revision
2. 数据集版本
3. 训练配置
4. adapter checkpoint
5. merged candidate
6. 完整评测报告

### 7.2 真相源

真相不认云机本地目录，只认：

- `W&B Artifacts`
- 对象存储

单机轮转场景下，本地磁盘只算缓存，不算归档。

### 7.3 命名建议

建议用统一命名：

- dataset: `turnplan-phase1@vYYYYMMDD-N`
- run: `tp14b-qlora-YYYYMMDD-seed42`
- adapter: `turnplan-qwen3-14b-adapter:<run_id>`
- merged: `turnplan-qwen3-14b-merged:<run_id>`
- report: `turnplan-eval:<run_id>`

## 8. 主评测口径

### 8.1 固定指标

主评测固定关注：

- `top_level_track_accuracy`
- `directive_accuracy`
- `all_null_accuracy`
- `knowledge_intent_accuracy`
- `task_command_family_accuracy`
- `flow_selection_accuracy`
- `slot_fill_exact_match`
- `json_valid_rate`
- `protocol_gate_pass_rate`

### 8.2 系统回放

不能只看模型文本输出，必须做完整回放：

1. 预测 `TurnPlan`
2. 送入 `protocol gate`
3. 再走 `state decision`
4. 再跑 `scenario replay`

因为这个项目真正重要的是：

- 有没有更稳地接住长对话
- 有没有减少误轨道
- 有没有让状态流转更稳定

不是单纯让 JSON 看起来更整齐。

### 8.3 晋级标准

候选模型要满足：

- 优于本地未微调 `Qwen3-14B`
- 不得在系统回放上明显差于当前远程基线
- 高价值 bucket 不允许显著回退
- `json_valid_rate` 和 `protocol_gate_pass_rate` 不能掉到不可接受水平

如果候选只在某几个容易的 bucket 漂亮，但整体回放变差，不晋级。

## 9. 其他轨道的风险与预防

这部分必须提前写死，不等上线后补救。

### 9.1 为什么其他轨道会受影响

虽然本轮只训练 `TurnPlan`，但最终部署是**整个项目统一切到同一个本地模型**。  
这意味着同一个底座要同时承担两类角色：

1. 结构化决策
2. 自然语言表达

而 `TurnPlan` 训练里最强的行为约束是：

- 只输出 JSON
- 不输出解释
- 不输出 markdown

这类约束如果泛化到表达层，就会带来副作用。

### 9.2 已知风险

统一替换后，`knowledge / clarify / chitchat` 可能出现：

- 回复异常简短
- 语气变硬
- 偶发 JSON 片段
- 解释意愿变弱
- 长上下文下表达不自然
- 本来该自然回答，却更像在“执行协议”

### 9.3 风险预防措施

#### 提示词隔离

`Planner` 与表达层必须使用不同 prompt，不允许混写成一套“万能提示词”。

表达层 prompt 要明确声明：

- 当前任务是自然语言回复
- 禁止输出 JSON、代码块、字段名
- 允许解释
- 给出 2 - 4 条风格示例

#### 推理参数隔离

建议固定两类调用参数：

- `Planner`
  - `temperature=0`
  - 较小 `max_tokens`
  - 强结构约束
- 表达层
  - `temperature=0.2 ~ 0.5`
  - 较宽 `max_tokens`
  - 优先自然表达

#### 输出守卫

对 `knowledge / clarify / chitchat` 增加轻量输出后检查：

- 若检测到明显 JSON 结构、字段名、代码块
- 自动重试一次
- 重试仍异常，则回退到蓝基线或固定话术兜底

这里的重点不是“补丁化修辞”，而是防止明显错误直接打到用户。

#### 轻评测

这三条轨道不单独做专项微调数据集，但必须做轻评测：

- `clarify`
  - 模糊意图
  - 补槽追问
  - 对象后续追问
- `knowledge`
  - 规则说明
  - 收费说明
  - 办理方式说明
- `chitchat`
  - 寒暄
  - 身份询问
  - 情绪表达

验收重点不是“多聪明”，而是：

- 不污染
- 不发硬
- 不拒答
- 不显著退化

## 10. 部署与切换

### 10.1 部署形态

统一模型服务一个主实例即可，不要求两套 14B 常驻。  
通过不同 prompt 和不同调用参数区分：

- `Planner`
- `knowledge`
- `clarify`
- `chitchat`

### 10.2 蓝绿切换

固定口径：

- 蓝：当前稳定基线
- 绿：本地微调候选

切换方式必须是配置切换，不是改代码常量。

### 10.3 上线顺序

上线顺序固定为：

1. 三套 baseline 完整评测
2. Pilot run
3. Main run
4. 主评测通过
5. 其他轨道轻评测通过
6. `scenario replay` 通过
7. 人工对话通过
8. 蓝绿切换

## 11. 回滚与灾备

### 11.1 回滚原则

如果出现以下情况，直接回滚蓝版本：

- TurnPlan 主评测不稳定
- 结构化输出污染到表达层
- 长对话回放明显退化
- 人工对话里出现频繁的 JSON 污染或僵硬回复

回滚时不做这些事：

- 不在坏 checkpoint 上继续训
- 不在上线环境现场改参数乱试
- 不删掉失败候选

### 11.2 正确动作

正确动作是：

1. 切回蓝版本
2. 保留失败 artifact
3. 对照数据版本、训练配置、评测报告复盘
4. 重新从冻结基座启动新一轮实验

## 12. 迁移与容器化

### 12.1 为什么必须容器化

你当前是单机轮转、卡位可能丢失的现实环境。  
这意味着：

- 机器不是资产
- 产物和流程才是资产

所以必须容器化，不然每次迁移都是重新搭环境。

但对当前 AutoDL 这台 30GB 系统盘机器，执行顺序要现实一点：

1. 先用直接 Python 环境把训练、评测、baseline 跑通
2. 再把 Docker data-root 挪到数据盘
3. 最后才在本机做 serving image

这样做不是退让，而是避免“容器化还没带来收益，系统盘先炸了”。

### 12.2 建议拆成两类镜像

- `trainer image`
  - PyTorch
  - CUDA
  - bitsandbytes
  - LLaMA-Factory
  - W&B
- `serving image`
  - vLLM
  - 模型挂载
  - healthcheck

### 12.3 新机器恢复动作

新机器只做四件事：

1. 拉镜像
2. 拉权重
3. 拉配置
4. 起服务

这四步之外的所有东西，都不应该依赖“上一台机器还活着”。

## 13. 本轮完成标准

本轮不是“把模型训过一次”就算完成，而是要满足：

- 训练链路跑通
- 三套 baseline 齐全
- 主评测口径固定
- 其他轨道轻评测与输出守卫到位
- 部署切换口径固定
- 回滚与迁移方案固定

满足这些条件后，这一轮微调工作才算真正进入“可持续迭代”的状态。
