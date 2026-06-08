from pathlib import Path
from typing import List, Dict, Any
import yaml

from atguigu.task.flow.flows import FlowList, FlowSlot, Flow
from atguigu.task.flow.steps import FlowStep, CollectedFlowStep


class FlowLoader:

    def load_many(self, paths: List[Path]) -> FlowList:
        """

        """
        flows: List[Flow] = []
        slots: Dict[str, FlowSlot] = {}
        for path in paths:
            loaded = self.load(path)
            flows.extend(loaded.flows)
            duplicate_slots = set(slots).intersection(loaded.slots)  # ① 检测重复槽位
            if duplicate_slots:
                duplicates = ", ".join(sorted(duplicate_slots))
                raise ValueError(
                    f"Duplicate slot definitions found across flow files: {duplicates}."
                )
            slots.update(loaded.slots)
        return FlowList(flows, slots)

    def load(self, path: Path) -> FlowList:
        """
        
        """
        # 1.打开文件
        with open(path, 'r', encoding='utf-8') as f:
            data: Dict[str, Any] = yaml.safe_load(f)

        # 2.加载slots
        slots: Dict[str, FlowSlot] = self._load_slots(data.get("slots", {}))

        # 3.加载folws
        flows = self._load_flows(data.get("flows", {}), slots)

        return FlowList(flows=flows, slots=slots)

    def _load_slots(self, slots_data: Dict[str, Any]) -> Dict[str, FlowSlot]:
        """

        """
        slots = {}
        for slot_name, slot_value in slots_data.items():
            slots[slot_name] = FlowSlot(
                name=slot_name,
                **slot_value
            )

        return slots

    def _load_flows(self, flows_data: Dict[str, Any], slots: Dict[str, FlowSlot]) -> List[Flow]:
        """

        """
        flows: List[Flow] = []

        for flow_id, flow_data in flows_data.items():
            steps = [FlowStep.from_dict(step) for step in flow_data.get("steps", [])]
            flows.append(Flow(
                id=flow_id,
                name=flow_data.get("name"),
                description=flow_data.get("description", ''),
                steps=steps,
                slots=self._collect_slots(slots, steps),
            ))

        return flows

    def _collect_slots(self, slots: Dict[str, FlowSlot], steps: List[FlowStep]) -> List[FlowSlot]:
        """

        """
        seen = set()
        flow_slots = []
        for step in steps:
            if not isinstance(step, CollectedFlowStep):
                continue

            # 流程中可能会在不同的step中有重复的槽位名字(LLM看流程使用的槽位：在同一个流程下 没有必要给LLM两份一样的槽位名字)
            step_slot_name = step.slot_name
            if step_slot_name in seen:
                continue  # 流程中有重复的槽位名字不添加
            seen.add(step_slot_name)
            slot_definition = slots.get(step_slot_name)

            if slot_definition is not None:  # 流程中有的槽位名字对应的槽位定义有
                flow_slots.append(slot_definition)

        return flow_slots


if __name__ == '__main__':
    base_path = Path(__file__).parents[3]
    user_flow_path = base_path / 'flow_config' / 'user_flows.yml'
    system_flow_path = base_path / 'flow_config' / 'system_flows.yml'
    loader = FlowLoader()
    flows_list = loader.load_many([user_flow_path, system_flow_path])
    print(flows_list)
