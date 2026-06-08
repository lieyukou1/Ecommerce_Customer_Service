# Stage01-数据层校验报告

## 1. 本次校验范围

本次报告为首份数据层基线校验报告，仅覆盖以下文件：

- `customer-service-backend/atuguigu/domain/messages.py`
- `customer-service-backend/atuguigu/domain/contexts.py`
- `customer-service-backend/atuguigu/domain/state.py`

说明：

- 本次不包含 `infrastructure/database.py`
- 本次不包含 `flow_config/` 配置文件
- 因为此前不存在同类校验报告，所以本报告作为首份基线报告

## 2. 当前结论

整体判断：

- 结构方向正确，已经基本沿着老师的 `domain` 层思路搭出了消息、上下文、状态三件套
- 物业语义迁移已开始落地，最明显的是 `DialogueState` 已统一为 `resident_id`
- 当前代码可以继续推进，但仍存在若干会影响后续运行、序列化兼容和边界一致性的逻辑风险

## 3. 关键问题清单

### [P1] `UserMessage` 已切换为 `resident_id`，但这意味着输入边界协议也被一起改名

位置：

- `customer-service-backend/atuguigu/domain/messages.py`

说明：

- `UserMessage` 已不再使用老师的 `sender_id`，而改为 `resident_id`
- 这不只是“状态层统一”，而是把消息层的输入口径也一起切掉了
- 如果后续前端或 API 层仍按 `sender_id` 传入，这里会直接不兼容

影响：

- 后续 API 入参、对象装配层、历史状态反序列化都必须明确跟随 `resident_id`
- 如果后面还要兼容现有前端 `sender_id`，需要单独设置装配层翻译，而不是指望 `from_dict()` 自动兼容

### [P1] `Session.to_dict()` 和 `Session.from_dict()` 的字段名不一致

位置：

- `customer-service-backend/atuguigu/domain/state.py:40-56`

说明：

- `Session` 实体字段名是 `started_at`
- 但 `to_dict()` 输出的是 `"start_at"`
- `from_dict()` 读取的却是 `"started_at"`

影响：

- 当前对象序列化后再反序列化，会出现字段名对不上
- 后续如果把 `DialogueState` 落库到 `dialogue_states`，这里会直接造成结构不一致

### [P1] `DialogueState.from_dict()` 对列表字段用 `data.get(...)` 但没有提供空列表默认值

位置：

- `customer-service-backend/atuguigu/domain/state.py:83-95`

说明：

- `paused_tasks=[... for paused_task in data.get("paused_tasks")]`
- `sessions=[... for session in data.get("sessions")]`

如果键不存在，`data.get(...)` 返回 `None`，随后列表推导会报错。

影响：

- 历史状态缺字段时无法稳妥反序列化
- 第一版落库或回放脏数据时容易炸在这里

### [P1] `resume_task()` 对空暂停栈没有保护

位置：

- `customer-service-backend/atuguigu/domain/state.py:126-140`

说明：

- 无论是 `if not flow_id` 分支还是兜底分支，都直接 `self.paused_tasks.pop()`
- 当没有暂停任务时，这里会抛异常

影响：

- 后续系统流恢复任务时，如果状态判断稍有偏差，就会在运行期直接报错

### [P2] `remove_slot()` 对 `active_task` 为空的情况没有保护

位置：

- `customer-service-backend/atuguigu/domain/state.py:168-173`

说明：

- 你已经对 slot 是否存在做了判断
- 但如果 `active_task` 本身是 `None`，仍然会先在 `self.active_task.slots` 处报错

影响：

- 当前问题不一定立刻暴露，但后面任务结束后又误删槽位时会触发

### [P2] `TaskContext.to_dict()` 直接返回原始 `slots` 引用

位置：

- `customer-service-backend/atuguigu/domain/contexts.py:11-16`

说明：

- 当前是 `"slots": self.slots`
- 这意味着返回值中的 `slots` 与对象内部持有的是同一个字典引用

影响：

- 如果后续外部代码修改 `to_dict()` 返回值中的 `slots`，可能反向污染上下文本体
- 与 `FocusedObject.attributes` 已做浅拷贝的处理不一致

## 4. 当前合理保留与后续关注点

当前可以保留、不必急着改的点：

1. `FocusedObject` 继续沿老师的对象消息结构保留 `id / type / title / attributes`
2. `TaskContext / SystemContext` 保持通用壳，不要急着做物业特化字段
3. `DialogueState.resident_id` 作为内部业务身份字段是合理的，符合物业语义

后续必须继续盯的点：

1. 消息层是否彻底统一成 `resident_id`，还是保留输入边界 `sender_id` 再在装配层翻译
2. `Session` 的序列化字段名必须尽快统一
3. `DialogueState` 的反序列化容错必须补齐，否则后面落库后会很脆
4. 任务中断、恢复、删槽位这些方法，后续进入真实运行流前要补最小防御

## 5. 校验基线说明

本报告为首份正式数据层基线校验报告。

后续同类报告默认遵循以下规则：

1. 活跃报告统一落在 `Material/Reports/`
2. 命名统一按阶段命名，例如：
   - `Stage01-数据层校验报告.md`
   - `Stage02-状态层校验报告.md`
   - `Stage03-服务层校验报告.md`
3. 同类报告默认只有最近一份算活跃，旧版移入 `Material/Archive/Reports/`
4. 后续增量报告默认只审查“上一份同类活跃校验报告落地之后新增或修改的目标代码”
5. 新报告开头必须明确：
   - 上一次对比基线是哪份报告
   - 本次实际覆盖的新增/修改文件范围是什么
