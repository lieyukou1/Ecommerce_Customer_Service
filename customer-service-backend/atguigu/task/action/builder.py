import importlib
import inspect
import pkgutil

from atguigu.task.action.base import Action
from atguigu.task.action.builtin.listener import ActionListener
from atguigu.task.action.builtin.response import ActionResponse
from atguigu.task.action.registry import ActionRegistry
from atguigu.task.action.runner import ActionRunner


def register_builtin_action(action_runner):
    """
    功能：把内置 action 注册进 runner。

    输入：
    - action_runner: 当前 action runner。

    输出：
    - 无返回值。

    调用情况：
    - `build_action_runner()`

    副作用：
    - 会把内置 action 写入 runner.registry。
    """
    action_listener = ActionListener()
    action_responser = ActionResponse()

    action_runner.registry.register(action_listener)
    action_runner.registry.register(action_responser)


def register_customer_action(action_runner):
    """
    功能：自动扫描 `task.action.custom` 包，并注册其中定义的 Action 子类。

    输入：
    - action_runner: 当前 action runner。

    输出：
    - 无返回值。

    调用情况：
    - `build_action_runner()`

    副作用：
    - 会 import 自定义 action 模块，并把扫描到的 action 实例写入注册表。
    """
    package = importlib.import_module("atguigu.task.action.custom")

    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):
        if is_pkg:
            continue

        module = importlib.import_module(module_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            # 只注册当前模块内真实声明的 Action 子类，避免把导入进来的基类或旁系类重复塞进去。
            if not issubclass(obj, Action) or obj is Action:
                continue
            if obj.__module__ != module.__name__:
                continue
            action_runner.registry.register(obj())


def build_action_runner():
    """
    功能：构造包含内置和自定义 action 的完整 runner。

    输入：
    - 无。

    输出：
    - ActionRunner: 已完成注册的动作执行器。

    调用情况：
    - 装配层创建 `TaskHandler` 时调用。

    副作用：
    - 会扫描并 import 自定义 action 包。
    """
    action_runner = ActionRunner(ActionRegistry())

    register_builtin_action(action_runner)
    register_customer_action(action_runner)

    return action_runner
