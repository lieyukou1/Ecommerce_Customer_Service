from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIR = ROOT / "canonical"
EXPORT_DIR = ROOT / "exports"
REPORT_DIR = ROOT / "reports"
HISTORY_DIR = ROOT / "history-backed"

ALLOWED_TOP_LEVEL_KEYS = {
    "id",
    "source",
    "bucket",
    "split",
    "input",
    "output",
    "meta",
    "semantic_meta",
    "audit_meta",
}
REQUIRED_TOP_LEVEL_KEYS = {
    "id",
    "source",
    "bucket",
    "split",
    "input",
    "output",
    "meta",
}
ALLOWED_INPUT_KEYS = {
    "history",
    "runtime_state",
    "active_task",
    "active_system_task",
    "paused_tasks",
    "focused_object",
    "user_message",
}
SEMANTIC_FAMILIES = {
    "continue_current_task",
    "start_or_switch_business_task",
    "read_only_request",
    "need_clarify",
    "exit_runtime",
    "social",
    "interrupt_resume_cancel",
}

BUCKET_SPECS = {
    "chitchat": {"train": 40, "val": 8},
    "directive_exit_runtime": {"train": 35, "val": 6},
    "ambiguous_all_null": {"train": 35, "val": 6},
    "service_item_knowledge": {"train": 55, "val": 10},
    "work_order_read_only_task": {"train": 85, "val": 16},
    "work_order_business_urge": {"train": 30, "val": 5},
    "work_order_business_complaint": {"train": 30, "val": 5},
    "active_task_slot_fill": {"train": 50, "val": 10},
    "object_context_followup": {"train": 45, "val": 7},
    "task_interrupt_resume_cancel": {"train": 45, "val": 7},
}

ALLOWED_OUTPUT_KEYS = {"task", "knowledge", "chitchat", "directive"}
ALLOWED_TASK_COMMANDS = {"start_flow", "resume_flow", "cancel_flow", "set_slots"}
ALLOWED_FLOW_IDS = [
    "work_order_status_query",
    "service_progress_tracking",
    "service_item_detail_query",
    "resident_work_orders_list_query",
    "resident_service_items_list_query",
    "resident_rule_qa",
    "work_order_urge_submission",
    "complaint_request_submission",
]
ALLOWED_KNOWLEDGE_INTENTS = [
    "service_item_info",
    "work_order_info",
    "property_fee_rule",
    "renovation_filing_rule",
    "parking_rule",
    "pet_rule",
    "community_rule",
    "general_property_info",
]

FLOW_MIN_COUNTS = {
    "work_order_status_query": 10,
    "service_progress_tracking": 10,
    "service_item_detail_query": 8,
    "resident_work_orders_list_query": 8,
    "resident_service_items_list_query": 8,
    "resident_rule_qa": 8,
    "work_order_urge_submission": 25,
    "complaint_request_submission": 25,
}

INTENT_MIN_COUNTS = {
    "service_item_info": 20,
    "work_order_info": 20,
    "property_fee_rule": 10,
    "renovation_filing_rule": 10,
    "parking_rule": 10,
    "pet_rule": 10,
    "community_rule": 10,
    "general_property_info": 10,
}

SYSTEM_PROMPT = """你是物业客服 TurnPlan 生成器。
你的唯一任务，是根据结构化上下文生成一个合法的 TurnPlan JSON。

输出合同必须严格满足：
1. 顶层只允许 task / knowledge / chitchat / directive 四个字段。
2. 一次只允许一个主轨道非空；如果方向不足以唯一判断，四个字段必须全为 null。
3. knowledge 的格式必须是 {"intents": ["intent_id"]}，其中 intents 是字符串数组，不是单个标量字段。
4. directive 当前只允许 {"action": "exit_runtime"}。
5. task.commands 当前只允许 start_flow / resume_flow / cancel_flow / set_slots。
6. start_flow 和 resume_flow 的 flow 标识字段名必须是 flow。
7. set_slots 的格式必须是 {"command": "set_slots", "slots": {...}}。
8. 只输出合法 JSON，不输出解释，不输出 markdown。

运行时判定补充：
1. 如果 active_system_task.flow_id == "system_collect_information"，优先判断用户是不是在继续补当前槽位。
2. 如果 active_task 不为空，优先判断是不是继续当前任务、补槽、确认或取消当前 flow。
3. 如果 focused_object 已经存在，围绕该对象的追问不要轻易退回 all-null。
4. 如果用户是在结束当前上下文、当前对象或当前这段办理链路，优先输出 directive.exit_runtime。

知识意图白名单：
- service_item_info
- work_order_info
- property_fee_rule
- renovation_filing_rule
- parking_rule
- pet_rule
- community_rule
- general_property_info

可用 flow 白名单：
- work_order_status_query
- service_progress_tracking
- service_item_detail_query
- resident_work_orders_list_query
- resident_service_items_list_query
- resident_rule_qa
- work_order_urge_submission
- complaint_request_submission
"""

WORK_ORDERS = [
    {
        "type": "work_order",
        "id": "WO20260601001",
        "title": "主卧空调不制冷",
        "attributes": {"status": "待上门", "amount": 80, "summary": "工程班已联系住户，今晚 19:30 上门检修。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601002",
        "title": "厨房水槽下方渗水",
        "attributes": {"status": "处理中", "amount": 60, "summary": "维修师傅已完成初检，等待更换软管配件。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601003",
        "title": "客厅灯路跳闸",
        "attributes": {"status": "待受理", "amount": 35, "summary": "电工班待确认是否需要更换空气开关。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601004",
        "title": "门禁卡失效",
        "attributes": {"status": "待受理", "amount": 20, "summary": "服务中心已收到工单，待安排门禁专员处理。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601005",
        "title": "卫生间排风异常",
        "attributes": {"status": "处理中", "amount": 45, "summary": "已安排电工复核排风机线路。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601006",
        "title": "阳台窗轨卡顿",
        "attributes": {"status": "待备件", "amount": 50, "summary": "需要补订滑轮配件，预计两天到货。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601007",
        "title": "书房网口无信号",
        "attributes": {"status": "待上门", "amount": 30, "summary": "弱电师傅已排期，明早 09:00 上门检查。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601008",
        "title": "楼道照明常亮",
        "attributes": {"status": "处理中", "amount": 0, "summary": "公区照明控制器已报修，等待更换模块。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601009",
        "title": "车位地锁无法升起",
        "attributes": {"status": "待上门", "amount": 55, "summary": "停车管理班今日下午统一巡检。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601010",
        "title": "北卧窗框渗风",
        "attributes": {"status": "待报价", "amount": 120, "summary": "门窗师傅已测量，等待密封条更换报价。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601011",
        "title": "玄关可视对讲无声",
        "attributes": {"status": "处理中", "amount": 40, "summary": "门禁专员已排查线路，等待主机复位。"},
    },
    {
        "type": "work_order",
        "id": "WO20260601012",
        "title": "儿童房窗帘电机卡死",
        "attributes": {"status": "待受理", "amount": 95, "summary": "智能家居维保组待确认电机型号。"},
    },
]

SERVICE_ITEMS = [
    {
        "type": "service_item",
        "id": "SVC2001",
        "title": "入户深度保洁",
        "attributes": {"price": 168, "description": "厨房、卫生间、客厅和卧室的整屋深度保洁。", "service_status": "可预约"},
    },
    {
        "type": "service_item",
        "id": "SVC2002",
        "title": "空调清洗",
        "attributes": {"price": 120, "description": "挂机与柜机的基础拆洗服务。", "service_status": "可预约"},
    },
    {
        "type": "service_item",
        "id": "SVC2003",
        "title": "门禁卡补办",
        "attributes": {"price": 50, "description": "线上登记后到服务中心领取新卡。", "service_status": "可办理"},
    },
    {
        "type": "service_item",
        "id": "SVC2004",
        "title": "窗纱更换",
        "attributes": {"price": 88, "description": "上门测量后更换窗纱及小五金。", "service_status": "可预约"},
    },
    {
        "type": "service_item",
        "id": "SVC2005",
        "title": "地漏疏通",
        "attributes": {"price": 69, "description": "针对卫生间和阳台地漏的基础疏通。", "service_status": "可预约"},
    },
    {
        "type": "service_item",
        "id": "SVC2006",
        "title": "燃气报警器换新",
        "attributes": {"price": 199, "description": "旧设备拆除与新设备安装调试。", "service_status": "可办理"},
    },
    {
        "type": "service_item",
        "id": "SVC2007",
        "title": "净水器滤芯更换",
        "attributes": {"price": 149, "description": "按机型上门更换滤芯并测试水质。", "service_status": "可预约"},
    },
    {
        "type": "service_item",
        "id": "SVC2008",
        "title": "可视对讲检修",
        "attributes": {"price": 90, "description": "检查室内机与门口机连接状态。", "service_status": "可预约"},
    },
]

RULE_TOPICS = [
    ("property_fee_rule", "物业费", "物业费按什么口径收"),
    ("renovation_filing_rule", "装修报备", "装修报备要准备什么材料"),
    ("parking_rule", "停车规则", "访客车怎么收费"),
    ("pet_rule", "宠物管理", "遛狗需要遵守哪些规定"),
    ("community_rule", "社区公约", "楼道堆物有什么限制"),
    ("general_property_info", "物业服务", "你们平时都能帮住户处理什么"),
]
