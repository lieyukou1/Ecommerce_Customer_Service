# Stage03-服务层校验报告

## 1. 本次校验范围

本报告为首份 Stage03 基线校验报告。

上一次对比基线：
- 无。当前不存在历史 `Stage03-服务层校验报告`

本次实际覆盖文件：
- `customer-service-backend/atuguigu/api/schemas.py`
- `customer-service-backend/atuguigu/api/router/chat_router.py`
- `customer-service-backend/atuguigu/api/dependencies.py`
- `customer-service-backend/atuguigu/service/dialogue_service.py`
- `customer-service-backend/atuguigu/engine/dialogue_engine.py`
- `customer-service-backend/atuguigu/repository/dialogue_state_repository.py`
- `customer-service-backend/atuguigu/model/base.py`
- `customer-service-backend/atuguigu/model/dialogue_state_record.py`
- `customer-service-backend/atuguigu/infrastructure/database.py`

说明：
- 本次重点是今天新增的 `api -> service -> engine -> repository -> model -> infrastructure` 主链
- 本次不覆盖更深一层的执行器实现、LLM 路由实现和物业中台对接实现

## 2. 当前结论

整体判断：
- 这条服务主链已经基本搭起来了，`resident_id` 口径也顺着老师主链打通了
- 之前会直接拦运行的几个问题已经收口，包括：
  - `ChatBotMessage` 已改成 `BaseModel`
  - `message_id` 已补默认生成
  - `repository` 与 `model` 的引用已对上
  - `get_dialogue_state_repository()` 已显式挂上 `Depends(get_session)`
- 当前代码已通过基础编译校验，`service / engine / repository / model` 的真实 import 链也能通过
- 但仍保留 2 个值得尽快清掉的定义风险，避免后面进入真实运行与持久化阶段时埋雷

## 3. 关键问题清单

### [P2] `ChatObject.attributes` 仍然使用可变默认值 `{}`，定义口径不稳

位置：
- `customer-service-backend/atuguigu/api/schemas.py:10`

现状：

```python
attributes: dict = {}
```

风险：
- 在 Pydantic 模型里这不一定立刻炸，但它不是当前最稳的定义方式
- 这类可变默认值容易把“默认配置”和“实例数据”混在一起理解，后面一旦字段结构变复杂，代码审查和维护成本会变差
- 你前面本来就是想把这块从 dataclass 语义切回 Pydantic 语义，这一步现在还没完全收口

建议：

```python
from pydantic import BaseModel, Field

attributes: dict = Field(default_factory=dict)
```

这不是为了抠风格，而是为了让接口层的数据定义语义稳定下来。

### [P2] `DialogueStateRecord.state_json` 的列默认值写成了 `{}`，类型语义不对

位置：
- `customer-service-backend/atuguigu/model/dialogue_state_record.py:13`

现状：

```python
state_json: Mapped[str] = mapped_column(TEXT, nullable=False, default={})
```

风险：
- `state_json` 当前建模是 `str`，数据库列类型也是 `TEXT`
- 但默认值写成了 Python 字典 `{}`，这在定义语义上是错位的
- 你现在的 repository 每次 save 都会显式传 `state_json`，所以暂时不一定触发
- 可一旦后面有别的插入路径、测试构造路径或 ORM 默认值回填路径依赖这个字段默认值，就可能在运行期出现类型不匹配或隐式转换问题

建议：
- 如果这列必须总是由 repository 显式写入，那就直接去掉默认值
- 如果一定要保留默认值，就至少改成字符串语义，例如：

```python
default="{}"
```

这里我更建议第一种，别给这个字段挂一个“看着像 JSON、实际是 Python dict”的假默认值。

## 4. 已确认收口的点

以下问题本轮已收口，可以先不再反复追：

1. `chat_router.py` 已统一使用 `resident_id`
2. `message_id` 已恢复默认生成逻辑
3. `ChatBotMessage` 已改为 `BaseModel`
4. `dependencies.py` 已显式声明 `Depends(get_session)`
5. `repository` 已切到 `atuguigu.model.dialogue_state_record`
6. `model/` 目录已补齐，`model -> repository -> service` 这条引用链能走通

## 5. 后续建议保留与继续关注点

当前可以先不动的点：

1. `DialogueService` 维持 `load -> engine -> save` 这个编排形状是合理的
2. `DialogueEngine` 现在先保留占位返回是正常的，它的责任是等待后续把路由和执行逻辑塞进去
3. `resident_id` 在这层已经统一下来了，不建议再回头混入 `sender_id`

下一层实现前建议继续盯的点：

1. `engine` 进入真实路由后，`ProcessResult` 生成是否继续只依赖 `user_message`，还是会受系统流/任务流上下文影响
2. `repository.save()` 当前是整包覆盖式持久化，后面如果会话历史变大，要注意状态 JSON 的体积和更新频率
3. `action.args` 的协议问题仍然存在于 Stage02 范围内，进入执行层前必须先统一

## 6. 校验基线说明

本报告为首份 `Stage03-服务层校验报告`，自此作为 Stage03 的活跃基线报告。

后续如果再次执行“写 Stage03-服务层校验报告”，默认规则为：
- 以上一份活跃版 `Stage03-服务层校验报告` 为增量比较基线
- 仅审查该报告落地之后新增或修改的目标代码
- 更新前先将当前活跃版归档到 `Material/Archive/Reports/`
