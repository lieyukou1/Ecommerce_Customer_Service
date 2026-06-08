READ_ONLY_QUERY_FLOW_IDS = {
    "work_order_status_query",
    "service_progress_tracking",
    "service_item_detail_query",
    "resident_work_orders_list_query",
    "resident_service_items_list_query",
    "resident_rule_qa",
}


def is_read_only_flow(flow_id: str | None) -> bool:
    """
    功能：判断一个 flow 是否属于只读查询型 flow。

    输入：
    - flow_id: 要判断的 flow 标识，可为空。

    输出：
    - bool: 在只读 flow 白名单中时返回 True。

    调用情况：
    - 由语义分类器调用，用于区分只读查询和业务办理。

    副作用：
    - 无。
    """
    return flow_id in READ_ONLY_QUERY_FLOW_IDS
