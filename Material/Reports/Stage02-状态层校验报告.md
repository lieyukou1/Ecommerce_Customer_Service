# Stage02-状态层校验报告

## 1. 本次校验范围

本报告为首份 Stage02 基线校验报告。

上一次对比基线：
- 无。当前不存在历史 `Stage02-状态层校验报告`

本次实际覆盖文件：
- `customer-service-backend/atuguigu/task/flow/steps.py`
- `customer-service-backend/atuguigu/task/flow/links.py`
- `customer-service-backend/atuguigu/task/flow/flows.py`
- `customer-service-backend/atuguigu/task/flow/loader.py`
- `customer-service-backend/flow_config/user_flows.yml`
- `customer-service-backend/flow_config/system_flows.yml`
- `customer-service-backend/atuguigu/domain/state.py`

说明：
- 本次重点是今天新增的流程定义层、流程装载层与受其影响的状态层接口
- 本次不覆盖执行器、服务编排层和 API 层

## 2. 当前结论

整体判断：
- 结构方向是对的，已经把老师 day03 新增的流程数据模型主骨架跟上了
- 今天修掉的 `resume_task()`、`set_slots()`、`remove_slot()` 边界问题是有效修正
- 当前代码已经通过基础编译校验，可继续推进下一层实现
- 但这轮仍保留 2 个需要尽早统一的设计点，其中 1 个属于运行期风险，1 个属于定义规范风险

## 3. 关键问题清单

### [P1] `system_collect_information` 的 `args` 结构与 `ActionFlowStep.args` 建模口径不一致

位置：
- `customer-service-backend/flow_config/system_flows.yml:116`
- `customer-service-backend/atuguigu/task/flow/steps.py:101-110`

现状：
- `ActionFlowStep.args` 当前按 `Dict[str, Any]` 建模
- 但 `system_collect_information` 这一步写的是：

```yaml
args: context.response
```

这意味着此处 `args` 实际是字符串，不是字典。

风险：
- 现在加载阶段虽然不会立刻炸，因为 `step_data.get("args", {})` 会原样接收这个字符串
- 但后续只要执行器按“动作参数一定是字典”来取值，例如 `step.args.get("text")`、`**step.args`、`for k, v in step.args.items()`，运行期就会直接报错
- 这类问题最烦的点在于：配置能加载成功，但会在真正执行系统流时才暴露

建议：
- 尽早统一 `action.args` 的协议，只选一种：
1. 全部强制为字典
2. 明确允许“表达式字符串”和“字典”双形态，并在 `ActionFlowStep` 类型与执行器里一起定义清楚

如果你想贴老师的“引用上下文对象”写法，那更稳的做法是把类型先放宽为：

```python
args: Dict[str, Any] | str = field(default_factory=dict)
```

然后在后续执行层明确区分两种分支，而不是默认它一定是字典。

### [P2] `kw_only=True` 虽然解决了 dataclass 继承报错，但带来了子类定义规范需要统一的问题

位置：
- `customer-service-backend/atuguigu/task/flow/steps.py:122-126`

现状：
- `CollectedFlowStep` 为了让 `response` 保持必填，同时绕开父类默认字段顺序限制，改成了：

```python
@dataclass(slots=True, kw_only=True)
class CollectedFlowStep(FlowStep):
    slot_name: str = ""
    response: ResponseDefinition
    validate: SlotValidation | None = None
```

这次改法本身是成立的，当前代码也能正常编译。

需要注意的规范问题：
- `kw_only=True` 不是“无代价修复”，它会把该 dataclass 的新增字段改成仅关键字传参
- 后面如果项目里别的步骤子类也遇到“父类有默认字段、子类又想新增必填字段”的情况，就必须统一口径
- 否则一部分子类是普通位置参数风格，一部分子类是关键字专用风格，后续手写构造、测试构造、工厂函数构造时会越来越乱

建议：
- 当前这版可以保留，不需要回退
- 但应当尽快在流程步骤层形成一个小规范：
  - 继承 `FlowStep` 且新增必填字段的子类，统一使用 `kw_only=True`
  - 后续手动构造步骤对象时，统一使用关键字参数，不混用位置参数
- 如果后面你觉得这种规范越来越别扭，再考虑在更高一层做工厂构造，而不是让外部直接 new 各种步骤对象

## 4. 已确认收口的点

以下问题本轮已收口，可以先不再反复追：

1. `links.py` 已正确区分 `StaticLink / ConditionalLink / FallbackLink`
2. `loader.py` 已补 `encoding='utf-8'`
3. `CollectedFlowStep.response` 不再使用错误的 `default_factory=ResponseDefinition`
4. `DialogueState.resume_task()` 已补空暂停栈与指定任务未命中的保护
5. `DialogueState.set_slots()` 与 `remove_slot()` 已补 `active_task is None` 的保护

## 5. 后续建议保留与继续关注点

当前可以先不动的点：

1. `flow_config/user_flows.yml` 的物业语义改写方向是对的
2. action 命名现在已经开始承担契约作用，后续不要随意改名
3. `CollectedFlowStep.response` 保持必填是合理的，不建议退回假默认值

下一层实现前建议继续盯的点：

1. 执行层到底如何解释 `action.args`
2. 系统流里的 `context.*` 表达式最终是由谁解析
3. `collect` 步骤拿到的 `response`、`validate` 后续是否需要统一的渲染/校验入口
4. `Session` 和 `DialogueState` 里 Stage01 尚未关闭的历史问题不要遗忘，尤其是旧状态序列化兼容性

## 6. 校验基线说明

本报告为首份 `Stage02-状态层校验报告`，自此作为 Stage02 的活跃基线报告。

后续如果再次执行“写 Stage02-状态层校验报告”，默认规则为：
- 以上一份活跃版 `Stage02-状态层校验报告` 为增量比较基线
- 仅审查该报告落地之后新增或修改的目标代码
- 更新前先将当前活跃版归档到 `Material/Archive/Reports/`
