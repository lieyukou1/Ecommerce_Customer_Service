from atguigu.task.action.base import Action


class ActionRegistry:
    """
    功能：维护 action name 到 Action 实例的映射。
    """

    def __init__(self):
        """
        功能：初始化空 action 注册表。

        输入：
        - 无。

        输出：
        - 无返回值。

        调用情况：
        - `build_action_runner()`

        副作用：
        - 初始化内部 `_actions` 字典。
        """
        self._actions: dict[str, Action] = {}

    def register(self, action: Action):
        """
        功能：注册一个 action 实例。

        输入：
        - action: 待注册的 action 实例。

        输出：
        - 无返回值。

        调用情况：
        - `register_builtin_action()`
        - `register_customer_action()`

        副作用：
        - 会覆盖同名 action 的注册项。
        """
        self._actions[action.name] = action

    def get(self, name: str) -> Action:
        """
        功能：按名称获取已注册 action。

        输入：
        - name: action 名称。

        输出：
        - Action: 对应的 action 实例。

        调用情况：
        - `ActionRunner.run()`

        副作用：
        - 无；名称不存在时抛出异常。
        """
        if name not in self._actions:
            raise KeyError(f"Action {name} not found")
        return self._actions[name]
