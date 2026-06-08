# TurnPlan 训练前 Baseline 执行清单

- 最后修改时间：2026-06-07
- 文档定位：TurnPlan 微调正式开跑前的 baseline、数据门禁、对照组与验收步骤清单
- 上级入口：[11_TurnPlan微调实施方案.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/11_TurnPlan微调实施方案.md)
- 环境入口：[13_AutoDL4090训练目录与落盘规范.md](/D:/Desktop/SGG_Project/Ecommerce_Customer_Service/Material/Finetune/turnplan_qwen3_14b/docs/13_AutoDL4090训练目录与落盘规范.md)

## 1. 这份清单解决什么问题

训练前最容易犯的错不是参数配错，而是：

- baseline 没留全
- 训练集和验证集心理上分开了，实际上风格高度泄漏
- 把“排列组合假多样性”当成模型提升
- 只看模型是否学会了训练集风格，没有看是否真的更适合项目链路

这份清单的目标就是：

**在正式训练前，把“我们到底在和谁比较、拿什么比较、哪些结果不可信”一次写死。**

## 2. 三套 baseline，缺一不可

### Baseline A：当前远程现网模型

用途：

- 代表当前项目真实线上水平
- 是“能不能替换现网”的直接参照物

记录内容：

- 模型名
- base_url
- 温度
- 评测时间
- 当次 prompt 版本

### Baseline B：本地未微调 `Qwen3-14B`

用途：

- 代表底座模型天然能力
- 用来回答“是不是不用微调也已经差不多”

记录内容：

- 基座模型 revision
- 推理参数
- prompt 版本
- 评测结果

### Baseline C：微调候选

用途：

- 表示本轮训练的真实增量

记录内容：

- run_id
- dataset version
- train config
- adapter / merged 路径
- 全套评测结果

## 3. baseline 前的数据门禁

在跑任何 baseline 之前，必须先确认数据集通过以下门禁：

### 3.1 结构门禁

- canonical schema 通过
- command 白名单通过
- intent 白名单通过
- 单轨或全 `null` 约束通过

### 3.2 真实性门禁

这里特别针对前面做数据集踩过的坑：

- 不允许再把“排列组合式句子”当作高质量样本
- 不允许再把明显模板残留的“比如……”句式混进主数据集
- 不允许再把“我是在补投诉原因”这类用户自我标注意图的样本混进训练或验证集
- 不允许把系统术语污染过重的样本当成自然语言样本

### 3.3 泄漏门禁

这一条必须单独看，因为它不是“有没有重复”这么简单。

验证集不允许与训练集共享下列高相似结构：

- 只换前缀/后缀的同一句核心表达
- 只换对象名、工单号、服务项名的模板句
- 同一 history 骨架 + 同一标签 + 极小文字改写
- 同一“写作口癖”成批复制，比如一连串都用“先按规则说明来”“最好把关键要求也带上”

如果验证集只是训练集的语言层弱改写，那么 baseline 和训练后对比都不可信。

## 4. baseline 评测分三层

### 4.1 层一：结构化离线评测

固定指标：

- `top_level_track_accuracy`
- `directive_accuracy`
- `all_null_accuracy`
- `knowledge_intent_accuracy`
- `task_command_family_accuracy`
- `flow_selection_accuracy`
- `slot_fill_exact_match`
- `json_valid_rate`
- `protocol_gate_pass_rate`

### 4.2 层二：系统级 replay

流程固定为：

1. 预测 `TurnPlan`
2. 送入 `protocol gate`
3. 送入 `state decision`
4. 跑 `scenario replay`

只有把 baseline 都放到同一条下游链路里，才能判断：

- 它到底是真的更适合当前项目
- 还是只是更像训练集的写法

### 4.3 层三：人工 smoke

人工 smoke 不是为了“多补点感觉”，而是为了补离线指标最容易漏掉的两类问题：

- 语言风格污染
- 长上下文下的真实使用体验

## 5. baseline 执行顺序

固定顺序如下：

1. 数据门禁通过
2. 先跑 Baseline A：远程现网模型
3. 再跑 Baseline B：本地未微调 `Qwen3-14B`
4. 整理对照报告
5. 再进入 pilot run

注意：

- **不能**先训练，再回头补基线
- **不能**只跑本地基座，不跑现网模型
- **不能**只看一组分数就开训

## 6. 这次 baseline 特别要防的“假提升”

### 6.1 排列组合假提升

如果验证集里大量样本只是：

- 同一句核心语义
- 换一批近义词
- 换一批对象名
- 换一点礼貌词

那么训练后的提升很可能只是在学“这套重写风格”，不是真理解。

### 6.2 重写器风格偏移假提升

因为这批数据经历过外部 LLM 语言层重写，所以 baseline 对比时要特别关注：

- 模型是不是只是在模仿重写器的风格
- 还是在真正提升 `TurnPlan` 决策

判断办法：

- 不能只看 canonical val
- 必须看 `scenario replay`
- 必须看 history-backed 样本
- 必须看人工 smoke

### 6.3 prompt 合同耦合假提升

如果本地基座和微调候选使用的 prompt 合同不同，那么结果不能直接比较。

因此 baseline 执行时固定要求：

- prompt 模板版本一致
- 输出合同一致
- 推理参数只在明确允许的范围内变化

## 7. baseline 报告最少要写什么

每套 baseline 跑完后，至少写清：

- 模型标识
- prompt 版本
- 评测时间
- 结构化指标
- replay 结果
- 人工 smoke 结论
- 是否存在明显污染或退化

建议每次 baseline 都在：

```text
/root/autodl-tmp/ecs-llm/baselines/<baseline_name>/
```

下保留：

- `config.json`
- `metrics.json`
- `summary.md`
- `smoke-notes.md`

## 8. baseline 通过标准

只要满足下面三条，baseline 阶段就算完成：

1. 现网模型与本地未训基座都已经完整留档
2. 离线指标、replay 和人工 smoke 三层都跑过
3. 已经能明确回答：
   - 当前现网和本地基座谁更强
   - 本地基座的短板主要在哪
   - 微调后真正应该盯哪几个指标

如果这三条还答不上来，就不要急着开训。
