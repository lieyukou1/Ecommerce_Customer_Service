from pathlib import Path
from typing import Any, Dict, List

import yaml

from atguigu.task.flow.flows import Flow, FlowList, FlowSlot
from atguigu.task.flow.steps import CollectedFlowStep, FlowStep


class FlowLoader:
    def load_many(self, paths: List[Path]) -> FlowList:
        """
        功能：加载多个 YAML flow 文件，并合并成一个 FlowList。

        输入：
        - paths: 要加载的 flow 配置文件路径列表。

        输出：
        - FlowList: 合并后的 flows 与 slots。

        调用情况：
        - 由装配层在启动时调用。

        副作用：
        - 无外部副作用；会在发现跨文件重复 slot 定义时抛错。
        """
        flows: List[Flow] = []
        slots: Dict[str, FlowSlot] = {}
        for path in paths:
            loaded = self.load(path)
            flows.extend(loaded.flows)
            # 跨文件重复 slot 定义会导致 planner 和执行层理解冲突，这里直接拒绝启动。
            duplicate_slots = set(slots).intersection(loaded.slots)
            if duplicate_slots:
                duplicates = ", ".join(sorted(duplicate_slots))
                raise ValueError(f"Duplicate slot definitions found across flow files: {duplicates}.")
            slots.update(loaded.slots)
        return FlowList(flows, slots)

    def load(self, path: Path) -> FlowList:
        """
        功能：加载单个 YAML flow 文件。

        输入：
        - path: 目标 YAML 文件路径。

        输出：
        - FlowList: 当前文件中声明的 flows 和 slots。

        调用情况：
        - 由 `load_many()` 调用，也可单独调试使用。

        副作用：
        - 会读取文件系统。
        """
        with open(path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f)

        slots: Dict[str, FlowSlot] = self._load_slots(data.get("slots", {}))
        flows = self._load_flows(data.get("flows", {}), slots)
        return FlowList(flows=flows, slots=slots)

    def _load_slots(self, slots_data: Dict[str, Any]) -> Dict[str, FlowSlot]:
        """
        功能：把 YAML 中的 slot 定义字典加载成 FlowSlot 映射。

        输入：
        - slots_data: `slots:` 节点下的原始字典。

        输出：
        - Dict[str, FlowSlot]: slot_name 到 FlowSlot 的映射。

        调用情况：
        - 由 `load()` 调用。

        副作用：
        - 无。
        """
        slots = {}
        for slot_name, slot_value in slots_data.items():
            slots[slot_name] = FlowSlot(name=slot_name, **slot_value)
        return slots

    def _load_flows(self, flows_data: Dict[str, Any], slots: Dict[str, FlowSlot]) -> List[Flow]:
        """
        功能：把 YAML 中的 flow 定义加载成 Flow 对象列表。

        输入：
        - flows_data: `flows:` 节点下的原始字典。
        - slots: 已加载好的全局 slot 定义。

        输出：
        - List[Flow]: 反序列化后的 flow 列表。

        调用情况：
        - 由 `load()` 调用。

        副作用：
        - 无。
        """
        flows: List[Flow] = []
        for flow_id, flow_data in flows_data.items():
            steps = [FlowStep.from_dict(step) for step in flow_data.get("steps", [])]
            flows.append(
                Flow(
                    id=flow_id,
                    name=flow_data.get("name"),
                    description=flow_data.get("description", ""),
                    steps=steps,
                    slots=self._collect_slots(slots, steps),
                )
            )
        return flows

    def _collect_slots(self, slots: Dict[str, FlowSlot], steps: List[FlowStep]) -> List[FlowSlot]:
        """
        功能：从某个 flow 的 steps 中抽取它真正会使用到的 slot 定义。

        输入：
        - slots: 全局 slot 定义映射。
        - steps: 当前 flow 的 step 列表。

        输出：
        - List[FlowSlot]: 当前 flow 实际使用的 slot 列表。

        调用情况：
        - 由 `_load_flows()` 调用。

        副作用：
        - 无。
        """
        seen = set()
        flow_slots = []
        for step in steps:
            if not isinstance(step, CollectedFlowStep):
                continue

            # 同一个 flow 内重复使用同名 collect slot 时，只保留一份定义给 planner 看。
            step_slot_name = step.slot_name
            if step_slot_name in seen:
                continue
            seen.add(step_slot_name)

            slot_definition = slots.get(step_slot_name)
            if slot_definition is not None:
                flow_slots.append(slot_definition)

        return flow_slots


if __name__ == "__main__":
    base_path = Path(__file__).parents[3]
    user_flow_path = base_path / "flow_config" / "user_flows.yml"
    system_flow_path = base_path / "flow_config" / "system_flows.yml"
    loader = FlowLoader()
    flows_list = loader.load_many([user_flow_path, system_flow_path])
    print(flows_list)
