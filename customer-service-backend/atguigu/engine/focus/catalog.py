import asyncio

from atguigu.domain.messages import FocusedObject
from atguigu.task.action.custom.api import request_property_api
from atguigu.task.action.custom.objects import build_service_item_object, build_work_order_object


class FocusedObjectCatalog:
    async def load_resident_candidates(self, resident_id: str) -> list[FocusedObject]:
        """
        功能：加载某个住户当前可被识别为 focused object 的候选对象列表。

        输入：
        - resident_id: 住户标识。

        输出：
        - list[FocusedObject]: 工单和服务项目合并后的候选对象列表。

        调用情况：
        - 由 `FocusedObjectResolver.try_switch_focused_object_from_text()` 调用。

        副作用：
        - 会并发请求物业中台接口。
        """
        work_orders_data, service_items_data = await asyncio.gather(
            request_property_api("GET", f"/residents/{resident_id}/work-orders"),
            request_property_api("GET", f"/residents/{resident_id}/service-items"),
        )

        candidates: list[FocusedObject] = []
        candidates.extend(self._build_work_order_candidates(work_orders_data))
        candidates.extend(self._build_service_item_candidates(service_items_data))
        return candidates

    @staticmethod
    def _build_work_order_candidates(work_orders_data: dict | None) -> list[FocusedObject]:
        """
        功能：把工单接口返回值转换成 FocusedObject 候选列表。

        输入：
        - work_orders_data: 工单接口返回的原始字典，可为空。

        输出：
        - list[FocusedObject]: 工单对象候选列表。

        调用情况：
        - 由 `load_resident_candidates()` 调用。

        副作用：
        - 无。
        """
        candidates: list[FocusedObject] = []
        for item in (work_orders_data or {}).get("work_orders") or []:
            if isinstance(item, dict):
                candidates.append(build_work_order_object(item))
        return candidates

    @staticmethod
    def _build_service_item_candidates(service_items_data: dict | None) -> list[FocusedObject]:
        """
        功能：把服务项目接口返回值转换成 FocusedObject 候选列表。

        输入：
        - service_items_data: 服务项目接口返回的原始字典，可为空。

        输出：
        - list[FocusedObject]: 服务项目对象候选列表。

        调用情况：
        - 由 `load_resident_candidates()` 调用。

        副作用：
        - 无。
        """
        candidates: list[FocusedObject] = []
        for item in (service_items_data or {}).get("service_items") or []:
            if isinstance(item, dict):
                candidates.append(build_service_item_object(item))
        return candidates
