from __future__ import annotations

import json
from collections import deque
from copy import deepcopy

from dataset_contract import ALLOWED_FLOW_IDS, RULE_TOPICS, SERVICE_ITEMS, WORK_ORDERS


def deep_clone(data):
    return deepcopy(data)


def mixed_pick(index: int, *banks):
    selections = []
    cursor = index
    for bank in banks:
        selections.append(bank[cursor % len(bank)])
        cursor //= len(bank)
    return selections


def history_from_turns(turns: list[tuple[str, str]]) -> list[dict]:
    history = []
    for user_text, assistant_text in turns:
        history.append({"role": "user", "text": user_text})
        history.append({"role": "assistant", "text": assistant_text})
    return history


def runtime_state(conversation_state: str, last_route: dict | None = None, last_task_outcome: dict | None = None) -> dict:
    return {
        "conversation_state": conversation_state,
        "last_route": last_route,
        "last_task_outcome": last_task_outcome,
    }


def task_state(flow_id: str, step_id: str, slots: dict | None = None) -> dict:
    return {
        "flow_id": flow_id,
        "step_id": step_id,
        "slots": slots or {},
    }


def make_input(
    *,
    history: list[dict],
    user_message: str,
    runtime: dict,
    focused_object: dict | None = None,
    active_task: dict | None = None,
    active_system_task: dict | None = None,
    paused_tasks: list[dict] | None = None,
) -> dict:
    return {
        "history": history,
        "runtime_state": runtime,
        "active_task": active_task,
        "active_system_task": active_system_task,
        "paused_tasks": paused_tasks or [],
        "focused_object": focused_object,
        "user_message": user_message,
    }


def make_record(
    *,
    bucket: str,
    split: str,
    index: int,
    source: str,
    input_payload: dict,
    output_payload: dict,
    primary_track: str,
    notes: str,
) -> dict:
    return {
        "id": f"tp_{bucket}_{split}_{index:03d}",
        "source": source,
        "bucket": bucket,
        "split": split,
        "input": input_payload,
        "output": output_payload,
        "meta": {
            "primary_track": primary_track,
            "notes": notes,
            "long_context": len(input_payload["history"]) >= 4,
        },
    }


def expand_quota_map(quota_map: dict[str, int]) -> list[str]:
    queue = deque((key, count) for key, count in quota_map.items() if count > 0)
    sequence: list[str] = []
    while queue:
        key, count = queue.popleft()
        sequence.append(key)
        if count > 1:
            queue.append((key, count - 1))
    return sequence


CHITCHAT_OPENERS = ["你好呀", "晚上好", "辛苦啦", "你在吗", "先打个招呼", "想跟你确认下你在不在", "嗨", "下午好"]
CHITCHAT_TOPICS = ["今天忙不忙", "你是谁", "你这边能做什么", "最近工单多吗", "你会不会转人工", "我先熟悉一下你", "你回复得挺快", "先认识一下"]
CHITCHAT_TONES = ["", "呀", "哈", "呢", "啊", "哦"]
CHITCHAT_HISTORIES = [
    [],
    history_from_turns([("你好", "你好，我在这边。")]),
    history_from_turns([("你是物业助手吗", "对，我是社区服务总台。"), ("那我先熟悉一下", "可以，你随时问我。")]),
    history_from_turns([("晚上好", "晚上好。"), ("今天工单多吗", "还在正常处理中。"), ("我先打个招呼", "好的。")]),
]

EXIT_MESSAGES = ["先这样", "退出当前这个", "先不看这个了", "重新开始", "这段先到这", "我先跳出去", "这一段先结束", "别围着这个说了"]
EXIT_SUFFIXES = ["，我想换个话题", "，稍后再说", "，先到这里", "，我先缓一缓", "，别继续这个上下文", "，我要重新起个头"]
AMBIGUOUS_MESSAGES = ["这个你帮我处理一下", "那你先看着办吧", "我想弄一下这个事", "这个怎么办呢", "你帮我安排一下", "这事你先接着", "我这边有个问题要处理", "先把这个给我办了"]
UNSUPPORTED_REQUESTS = ["帮我改门牌显示名称", "直接开小区发票", "给我查邻居装修进度", "帮我改产权登记", "把访客权限永久开通", "给我远程重置门锁密码"]

SERVICE_INFO_ASPECTS = ["收费和办理方式", "服务范围和收费", "预约状态和上门时间", "办理地点和领取方式", "材料要求和收费", "服务说明和注意事项"]
WORK_ORDER_INFO_MESSAGES = ["这条工单是报什么问题来着", "把这单的内容给我概括一下", "这单当时记录了什么情况", "这条工单的背景再说一遍", "我想先了解一下这单本身"]
READ_ONLY_MESSAGES = ["这个现在什么状态", "处理到哪一步了", "进度卡在哪了", "费用怎么算", "是不是还在等配件", "上门时间定了没"]
READ_ONLY_PREFIXES = ["我想确认一下", "你直接告诉我", "先帮我看下", "麻烦查一下", "顺带问下", "我重点想知道"]
READ_ONLY_SUFFIXES = ["", "，别只说大概", "，我想听具体点", "，别串到别的工单", "，按这单本身回答就行"]
READ_ONLY_QUERY_TAILS = ["", "，先按当前对象说", "，我只关心这一个", "，别跳到其他记录", "，这轮先查清楚再说"]

URGE_MESSAGES = ["那先帮我催一下", "直接催办这单", "先替我跟进催一下", "这个得赶紧催办", "帮我把这单往前推一推"]
URGE_REASONS = ["家里老人怕热", "漏水越来越严重", "孩子晚上睡不好", "门禁刷不开很耽误事", "希望今天尽快处理", "已经影响正常做饭了", "晚上还要继续住人"]
URGE_SUFFIXES = ["，麻烦快一点", "，别让我再追着问", "，尽量今天推进", "，我这边真的挺着急", "，这次别再拖了"]

COMPLAINT_MESSAGES = ["这单我要投诉", "直接帮我发起投诉", "这次我得正式投诉一下", "我对这单处理不满意，要投诉", "别只催办了，我要投诉"]
COMPLAINT_REASONS = ["处理太慢了", "已经影响正常进出", "反复报修还没解决", "沟通后一直没反馈", "预约时间一拖再拖", "说好上门又放了鸽子", "现场处理完问题还是在"]
COMPLAINT_SUFFIXES = ["，我已经有点不满了", "，这个体验太差了", "，请按正式投诉处理", "，别再只口头安抚我了", "，我要留个明确记录"]

RULE_KNOWLEDGE_TEMPLATES = ["想了解一下{topic_label}的规则", "{topic_label}这块是怎么规定的", "给我说说{topic_label}的要求", "{topic_label}一般按什么标准执行", "先介绍下{topic_label}相关说明"]
RULE_TASK_TEMPLATES = ["帮我查一下{topic_label}规则", "把{topic_label}这块给我调出来", "按物业规则问答看下{topic_label}", "我现在要查{topic_label}规定"]
GENERAL_PROPERTY_MESSAGES = [
    "你们平时都能帮住户处理什么",
    "先整体介绍一下你们物业助手能覆盖哪些事",
    "我想知道你们通常能处理哪些住户问题",
    "别说具体工单，先讲讲你们服务范围",
    "先给我一个整体能力介绍",
]

LIST_FLOW_MESSAGES = {
    "resident_work_orders_list_query": ["把我最近的工单列一下", "我名下现在有哪些工单", "先给我看一下当前工单列表", "把还没完结的工单都列出来"],
    "resident_service_items_list_query": ["把能办的服务项目列一下", "我这边当前能看的服务项目有哪些", "先给我看一下常用服务项目", "把可预约的服务项目发我看下"],
}
SERVICE_ITEM_DETAIL_MESSAGES = ["把这个项目详细介绍一下", "我想看这个服务项目的完整详情", "这个项目具体是什么内容", "把这个服务项的状态和价格都说清楚"]
RULE_FOLLOWUP_TEMPLATES = ["刚才那类{topic_label}规则，再展开讲一下", "{topic_label}这块你再说细一点", "别只给结论，把{topic_label}的规则依据也讲一下", "关于{topic_label}，你顺着刚才的话题再补充一下"]
SERVICE_FOLLOWUP_PREFIXES = ["那", "顺着刚才这个", "基于你刚才说的", "围绕当前项目"]
INTERRUPT_MESSAGES = {
    "resume": ["继续刚才那个催办", "把刚才那单催办接着办", "回到刚才的催办流程", "刚才那个催办别断，继续"],
    "cancel": ["这次投诉先取消", "当前这条投诉我先撤掉", "这轮投诉先别提了", "把眼下这个投诉流程停掉"],
    "switch_to_complaint": ["催办先放着，我要投诉这单处理太慢", "先别催办了，这单我要正式投诉", "当前催办先停，我改成投诉处理太慢", "这次别只催办，我要转投诉"],
    "switch_to_urge": ["投诉先停一下，改成催办这单，家里老人怕热", "先别走投诉了，改成催办，家里老人怕热", "投诉流程先放着，我现在更想催办这单", "这单先不投诉了，先催办，情况比较急"],
}

ACTIVE_SLOT_VARIANTS = [
    ("work_order_urge_submission", "collect_urge_reason", "urge_reason", ["原因就是{reason}", "催办原因是{reason}", "因为{reason}", "{reason}，麻烦尽快处理"]),
    ("complaint_request_submission", "collect_complaint_reason", "complaint_reason", ["投诉原因就是{reason}", "原因是{reason}", "我不满意主要因为{reason}", "{reason}，所以我要投诉"]),
    ("complaint_request_submission", "collect_complaint_confirm", "complaint_confirm", ["确认提交", "我确认投诉", "对，提交吧", "确认，现在就提交"]),
    ("work_order_urge_submission", "collect_contact_phone", "contact_phone", ["联系电话是{phone}", "你记一下我的手机号 {phone}", "留这个电话 {phone}", "回访打 {phone} 就行"]),
    ("complaint_request_submission", "collect_contact_phone", "contact_phone", ["投诉联系号码是{phone}", "你按这个电话回访 {phone}", "留个投诉联系电话 {phone}", "后续联系我用 {phone}"]),
    ("resident_rule_qa", "collect_rule_topic", "rule_topic", ["我想查{topic_label}", "先看{topic_label}这块", "就是{topic_label}相关规定", "查{topic_label}"]),
    ("service_item_detail_query", "collect_service_item_id", "service_item_id", ["看{service_title}这个项目", "就查{service_title}", "{service_title}这个", "查一下{service_title}详情"]),
]

COMPLAINT_CANCEL_MESSAGES = [
    "算了，这条投诉先别提交",
    "我先不正式投诉了，把这条流程停掉",
    "先撤回这次投诉确认",
    "这一步先别提交投诉，我想再看看",
]


def object_focus_history(obj: dict, mode: str, length: int, variant: int = 0) -> list[dict]:
    if mode == "service_item":
        history_banks = [
            [
                (f"我刚点开了{obj['title']}", f"好的，当前可以围绕{obj['title']}继续咨询。"),
                ("我先看看这个项目", "可以继续问收费、办理方式、服务说明或预约状态。"),
                ("你先别跳别的", f"明白，我先只围绕{obj['title']}回答。"),
            ],
            [
                (f"{obj['title']}这个服务我刚看到", f"好，我先把焦点固定在 {obj['title']}。"),
                ("我想先摸清办理条件", "可以，我会优先解释收费、材料和办理入口。"),
                (f"如果这个项目能办再说下一步", f"明白，先不切到别的服务，当前状态是 {obj['attributes']['service_status']}。"),
            ],
            [
                (f"我现在只看{obj['title']}", f"收到，先围绕 {obj['title']} 的信息讲清楚。"),
                ("先别扯到工单去", "没问题，这一段只按服务项目来回答。"),
                ("后面要不要办我再决定", f"可以，先把 {obj['title']} 的说明和价格给你讲明白。"),
            ],
            [
                (f"{obj['title']}我已经选中了", f"好的，这个项目目前显示为 {obj['attributes']['service_status']}。"),
                ("你就顺着这个项目往下说", "可以，我会按当前选中的服务项目继续。"),
                ("别切到别的对象", f"明白，焦点对象保持为 {obj['id']}。"),
            ],
        ]
    else:
        history_banks = [
            [
                (f"我在看{obj['title']}这条工单", "好的，当前可以继续问状态、进度、费用或办理。"),
                ("先围着这单说", "没问题，我先不切别的话题。"),
                ("我怕你串单", f"不会，我现在焦点就是{obj['id']}。"),
            ],
            [
                (f"{obj['title']}这单我刚打开", f"收到，我先锁定工单 {obj['id']}。"),
                ("你先别跳到其他报修", "明白，我只围绕这条工单继续。"),
                (f"这单现在是什么状态你也记着", f"记着，当前摘要是：{obj['attributes']['summary']}"),
            ],
            [
                (f"我现在只关心{obj['title']}", f"好，焦点就放在这条工单上。"),
                ("别把其他单带进来", "不会，我先保持当前对象不变。"),
                (f"上次你说它是{obj['attributes']['status']}", "对，我会沿着这条状态继续回答。"),
            ],
            [
                (f"这条{obj['title']}我还在跟进", f"明白，我先沿当前工单链路继续。"),
                ("后面如果要切任务我会单说", "好，现在先不改对象、不换工单。"),
                (f"你把单号也记住", f"已经记住，是 {obj['id']}。"),
            ],
        ]
    turns = history_banks[variant % len(history_banks)]
    return [] if length <= 0 else history_from_turns(turns[: length // 2])


def general_history(mode: str, length: int, index: int, variant: int = 0) -> list[dict]:
    history_bank = {
        "knowledge": [
            [("我有点物业方面的问题", "可以，你直接说。")],
            [("我先咨询点规则", "好的。"), ("我不急着办业务", "明白，我先按咨询来。")],
            [("我在想要不要办", "可以先了解。"), ("先别直接给我开流程", "好的，我先解释信息。"), ("我再决定", "明白。")],
            [("我这次先问信息，不急着办理", "好，我先按知识咨询来处理。"), ("如果需要办业务我后面再说", "可以，先把规则和说明讲清楚。"), ("别默认给我开流程", "明白，优先走问答。")] ,
            [("我现在主要是想问清政策", "收到，我先不把它当成办理请求。"), ("先帮我把背景讲明白", "可以，我会先解释规则或服务信息。"), ("等我听完再决定下一步", "好的。")] ,
        ],
        "all_null": [
            [("我想办点事", "可以，你先说具体一点。")],
            [("我有个事情", "你可以再具体描述一下。"), ("和家里服务有关", "明白，你继续说。")],
            [("我不是很会说", "没事，我来配合你。"), ("反正就是有个问题", "你可以先说是工单、服务项目还是规则。"), ("我再组织一下", "可以。")],
            [("我这边有点事想处理", "没问题，你先说清是查信息还是办理业务。"), ("我怕自己描述不准", "没关系，你先给我一个方向。"), ("我想到哪儿说到哪儿", "可以，我会帮你收拢。")] ,
            [("我一时半会儿说不完整", "没关系，我们先把范围缩小。"), ("大概是物业这边的事", "明白，你可以再说具体对象或诉求。"), ("你先别替我决定", "好，我先等你补全信息。")] ,
        ],
    }
    bank = history_bank[mode]
    return [] if length <= 0 else history_from_turns(bank[(index + variant) % len(bank)][: length // 2])


def build_chitchat_record(split: str, index: int, offset: int) -> dict:
    opener, topic, tone, history = mixed_pick(offset + index, CHITCHAT_OPENERS, CHITCHAT_TOPICS, CHITCHAT_TONES, CHITCHAT_HISTORIES)
    return make_record(
        bucket="chitchat",
        split=split,
        index=index,
        source="hand-crafted",
        input_payload=make_input(history=history, user_message=f"{opener}{tone}，{topic}", runtime=runtime_state("IDLE")),
        output_payload={"task": None, "knowledge": None, "chitchat": {}, "directive": None},
        primary_track="chitchat",
        notes="pure chitchat",
    )


def build_directive_record(split: str, index: int, offset: int) -> dict:
    context_kinds = ["knowledge_service", "knowledge_work_order", "active_urge", "active_complaint", "read_only_task", "collect_slot"]
    context_kind, message, suffix, work_order, history_length = mixed_pick(offset + index, context_kinds, EXIT_MESSAGES, EXIT_SUFFIXES, WORK_ORDERS, [0, 2, 4, 6])
    focused_object = None
    active_task = None
    active_system_task = None
    last_route = None
    last_outcome = None
    conversation_state = "IDLE"
    exit_hint = ""
    if context_kind == "knowledge_service":
        service_item = deep_clone(SERVICE_ITEMS[(offset + index) % len(SERVICE_ITEMS)])
        focused_object = service_item
        history = object_focus_history(service_item, "service_item", history_length, offset + index // len(SERVICE_ITEMS))
        last_route = {"track": "knowledge", "semantic_kind": "knowledge"}
        conversation_state = "FOCUSED_KNOWLEDGE"
        exit_hint = f"{service_item['title']}这段先收住"
    elif context_kind == "knowledge_work_order":
        focused_object = deep_clone(work_order)
        history = object_focus_history(work_order, "work_order", history_length, offset + index // len(WORK_ORDERS))
        last_route = {"track": "knowledge", "semantic_kind": "knowledge"}
        conversation_state = "FOCUSED_KNOWLEDGE"
        exit_hint = f"{work_order['title']}这条先不继续"
    elif context_kind == "active_urge":
        focused_object = deep_clone(work_order)
        history = object_focus_history(work_order, "work_order", history_length, offset + index // len(WORK_ORDERS))
        active_task = task_state("work_order_urge_submission", "collect_urge_reason", {"work_order_id": work_order["id"]})
        last_route = {"track": "task", "semantic_kind": "business_task"}
        last_outcome = {"semantic_kind": "business_task"}
        conversation_state = "ACTIVE_TASK"
        exit_hint = f"{work_order['title']}这条催办先停"
    elif context_kind == "active_complaint":
        focused_object = deep_clone(work_order)
        history = object_focus_history(work_order, "work_order", history_length, offset + index // len(WORK_ORDERS))
        active_task = task_state("complaint_request_submission", "collect_complaint_confirm", {"work_order_id": work_order["id"], "complaint_reason": COMPLAINT_REASONS[(offset + index) % len(COMPLAINT_REASONS)]})
        last_route = {"track": "task", "semantic_kind": "business_task"}
        last_outcome = {"semantic_kind": "business_task"}
        conversation_state = "ACTIVE_TASK"
        exit_hint = f"{work_order['title']}这条投诉先放下"
    elif context_kind == "read_only_task":
        focused_object = deep_clone(work_order)
        history = object_focus_history(work_order, "work_order", history_length, offset + index // len(WORK_ORDERS))
        active_task = task_state(ALLOWED_FLOW_IDS[(offset + index) % 2], "end", {"work_order_id": work_order["id"]})
        last_route = {"track": "task", "semantic_kind": "read_only_query"}
        last_outcome = {"semantic_kind": "read_only_query"}
        conversation_state = "ACTIVE_TASK"
        exit_hint = f"{work_order['title']}这条查询先结束"
    else:
        focused_object = deep_clone(work_order)
        history = object_focus_history(work_order, "work_order", history_length, offset + index // len(WORK_ORDERS))
        active_task = task_state("work_order_urge_submission", "collect_urge_reason", {"work_order_id": work_order["id"]})
        active_system_task = task_state("system_collect_information", "listen", {"target_slot": "urge_reason"})
        last_route = {"track": "task", "semantic_kind": "business_task"}
        last_outcome = {"semantic_kind": "business_task"}
        conversation_state = "ACTIVE_TASK"
        exit_hint = f"{work_order['title']}这条补信息先停一下"
    message = f"{message}{suffix}，{exit_hint}"
    return make_record(
        bucket="directive_exit_runtime",
        split=split,
        index=index,
        source="repo-scenario" if context_kind in {"active_urge", "active_complaint", "collect_slot"} else "hand-crafted",
        input_payload=make_input(
            history=history,
            user_message=f"{message}{suffix}",
            runtime=runtime_state(conversation_state, last_route, last_outcome),
            focused_object=focused_object,
            active_task=active_task,
            active_system_task=active_system_task,
        ),
        output_payload={"task": None, "knowledge": None, "chitchat": None, "directive": {"action": "exit_runtime"}},
        primary_track="directive",
        notes=f"exit current runtime from {context_kind}",
    )


def build_ambiguous_record(split: str, index: int, offset: int) -> dict:
    work_order = deep_clone(WORK_ORDERS[(offset + index) % len(WORK_ORDERS)])
    service_item = deep_clone(SERVICE_ITEMS[(offset + index) % len(SERVICE_ITEMS)])
    states = [
        ("IDLE", None, None, None, None, []),
        ("CLARIFYING", {"track": "clarify", "semantic_kind": "clarify"}, None, None, None, []),
        ("FOCUSED_KNOWLEDGE", {"track": "knowledge", "semantic_kind": "knowledge"}, None, service_item, None, []),
        ("ACTIVE_TASK", {"track": "task", "semantic_kind": "business_task"}, {"semantic_kind": "business_task"}, work_order, task_state("work_order_urge_submission", "collect_urge_reason", {"work_order_id": work_order["id"]}), []),
        ("TRANSITIONING", {"track": "task", "semantic_kind": "interrupted"}, {"semantic_kind": "business_task"}, work_order, None, [task_state("work_order_urge_submission", "collect_urge_reason", {"work_order_id": work_order["id"]})]),
    ]
    state_name, last_route, last_outcome, focused_object, active_task, paused_tasks = states[(offset + index) % len(states)]
    message, unsupported, history_length = mixed_pick(offset + index, AMBIGUOUS_MESSAGES, UNSUPPORTED_REQUESTS, [0, 2, 4, 6])
    return make_record(
        bucket="ambiguous_all_null",
        split=split,
        index=index,
        source="hand-crafted",
        input_payload=make_input(
            history=general_history("all_null", history_length, offset + index),
            user_message=f"{message}，比如{unsupported}",
            runtime=runtime_state(state_name, last_route, last_outcome),
            focused_object=focused_object,
            active_task=active_task,
            paused_tasks=paused_tasks,
        ),
        output_payload={"task": None, "knowledge": None, "chitchat": None, "directive": None},
        primary_track="all_null",
        notes="ambiguous or unsupported request",
    )


def build_service_item_knowledge_record(split: str, index: int, offset: int, intent_sequence: list[str]) -> dict:
    intent = intent_sequence[index]
    history_length = [0, 2, 4, 6][(offset + index) % 4]
    seed = offset + index * 3
    rule_tail = "也把适用对象和注意点说清楚" if split == "val" else "最好把关键要求也带上"
    if intent == "service_item_info":
        service_item = deep_clone(SERVICE_ITEMS[(offset + index) % len(SERVICE_ITEMS)])
        aspect = SERVICE_INFO_ASPECTS[(offset + index) % len(SERVICE_INFO_ASPECTS)]
        templates = [
            "{title}的{aspect}都说一下",
            "我想把{title}的{aspect}一次问清",
            "{title}这个项目，重点讲讲{aspect}",
            "围绕{title}，把{aspect}展开说明",
            "先别讲别的，就说{title}的{aspect}",
        ]
        message = templates[(seed + (1 if split == "val" else 0)) % len(templates)].format(title=service_item["title"], aspect=aspect)
        history = object_focus_history(service_item, "service_item", history_length, offset + index // len(SERVICE_ITEMS))
        focused_object = service_item
        source = "repo-scenario"
    else:
        topic_map = {topic_intent: (topic_label, default_question) for topic_intent, topic_label, default_question in RULE_TOPICS}
        topic_label, default_question = topic_map[intent]
        if intent == "general_property_info":
            wrappers = ["", "先不聊具体工单，", "我这轮先问整体能力，", "如果不办业务的话，"]
            tails = ["", "，先按服务边界讲", "，别落到具体业务办理", "，先讲整体能力地图"]
            message = f"{wrappers[(seed + (1 if split == 'val' else 0)) % len(wrappers)]}{GENERAL_PROPERTY_MESSAGES[(seed // 2) % len(GENERAL_PROPERTY_MESSAGES)]}{tails[(seed // 3 + (1 if split == 'val' else 0)) % len(tails)]}"
        else:
            lead_ins = ["", "这轮我只是咨询，", "先按规则说明来，", "别默认进入办理，"]
            message = f"{lead_ins[(seed + (1 if split == 'val' else 0)) % len(lead_ins)]}{RULE_KNOWLEDGE_TEMPLATES[(seed // 2) % len(RULE_KNOWLEDGE_TEMPLATES)].format(topic_label=topic_label)}，{rule_tail}"
        history = general_history("knowledge", history_length, offset + index, variant=offset + index)
        focused_object = None
        source = "hand-crafted"
    return make_record(
        bucket="service_item_knowledge",
        split=split,
        index=index,
        source=source,
        input_payload=make_input(
            history=history,
            user_message=message,
            runtime=runtime_state("FOCUSED_KNOWLEDGE" if focused_object else "IDLE", {"track": "knowledge", "semantic_kind": "knowledge"}, None),
            focused_object=focused_object,
        ),
        output_payload={"task": None, "knowledge": {"intents": [intent]}, "chitchat": None, "directive": None},
        primary_track="knowledge",
        notes=f"knowledge intent {intent}",
    )


def build_read_only_task_record(split: str, index: int, offset: int, flow_sequence: list[str]) -> dict:
    flow_id = flow_sequence[index]
    history_length = [0, 2, 4, 6][(offset + index) % 4]
    read_seed = offset + index + index // 4
    prefix = READ_ONLY_PREFIXES[read_seed % len(READ_ONLY_PREFIXES)]
    suffix = READ_ONLY_SUFFIXES[(read_seed // 2) % len(READ_ONLY_SUFFIXES)]
    query_tail = READ_ONLY_QUERY_TAILS[(read_seed // 5) % len(READ_ONLY_QUERY_TAILS)]
    if flow_id in {"work_order_status_query", "service_progress_tracking"}:
        work_order = deep_clone(WORK_ORDERS[(offset + index) % len(WORK_ORDERS)])
        message = f"{prefix}{work_order['title']}这单{READ_ONLY_MESSAGES[(read_seed // 3) % len(READ_ONLY_MESSAGES)]}{suffix}{query_tail}"
        history = object_focus_history(work_order, "work_order", history_length, offset + index // len(WORK_ORDERS))
        focused_object = work_order
        commands = [{"command": "start_flow", "flow": flow_id}, {"command": "set_slots", "slots": {"work_order_id": work_order["id"]}}]
    elif flow_id == "service_item_detail_query":
        service_item = deep_clone(SERVICE_ITEMS[(offset + index) % len(SERVICE_ITEMS)])
        message = f"{prefix}{service_item['title']}{SERVICE_ITEM_DETAIL_MESSAGES[(read_seed // 3) % len(SERVICE_ITEM_DETAIL_MESSAGES)]}{suffix}{query_tail}"
        history = object_focus_history(service_item, "service_item", history_length, offset + index // len(SERVICE_ITEMS))
        focused_object = service_item
        commands = [{"command": "start_flow", "flow": flow_id}, {"command": "set_slots", "slots": {"service_item_id": service_item["id"]}}]
    elif flow_id == "resident_work_orders_list_query":
        message = f"{prefix}{LIST_FLOW_MESSAGES[flow_id][(read_seed // 3) % len(LIST_FLOW_MESSAGES[flow_id])]}{suffix}{query_tail}"
        history = general_history("knowledge", history_length, offset + index, variant=offset + index)
        focused_object = None
        commands = [{"command": "start_flow", "flow": flow_id}]
    elif flow_id == "resident_service_items_list_query":
        message = f"{prefix}{LIST_FLOW_MESSAGES[flow_id][(read_seed // 3) % len(LIST_FLOW_MESSAGES[flow_id])]}{suffix}{query_tail}"
        history = general_history("knowledge", history_length, offset + index, variant=offset + index)
        focused_object = None
        commands = [{"command": "start_flow", "flow": flow_id}]
    else:
        _, topic_label, _ = RULE_TOPICS[(offset + index) % len(RULE_TOPICS)]
        message = f"{prefix}{RULE_TASK_TEMPLATES[(read_seed // 3) % len(RULE_TASK_TEMPLATES)].format(topic_label=topic_label)}{suffix}{query_tail}"
        history = general_history("knowledge", history_length, offset + index, variant=offset + index)
        focused_object = None
        commands = [{"command": "start_flow", "flow": flow_id}, {"command": "set_slots", "slots": {"rule_topic": topic_label}}]
    return make_record(
        bucket="work_order_read_only_task",
        split=split,
        index=index,
        source="repo-scenario" if focused_object is not None else "hand-crafted",
        input_payload=make_input(
            history=history,
            user_message=message,
            runtime=runtime_state("FOCUSED_KNOWLEDGE" if focused_object else "IDLE", {"track": "task", "semantic_kind": "read_only_query"}, {"semantic_kind": "read_only_query"}),
            focused_object=focused_object,
        ),
        output_payload={"task": {"commands": commands}, "knowledge": None, "chitchat": None, "directive": None},
        primary_track="task",
        notes=f"read-only task flow {flow_id}",
    )


def build_urge_record(split: str, index: int, offset: int) -> dict:
    work_order = deep_clone(WORK_ORDERS[(offset + index) % len(WORK_ORDERS)])
    reason = URGE_REASONS[(offset * 2 + index) % len(URGE_REASONS)]
    prefixes = ["", f"{work_order['title']}这单", "围绕当前这条工单，", f"{work_order['id']}这单"]
    message = f"{prefixes[(offset + index + (1 if split == 'val' else 0)) % len(prefixes)]}{URGE_MESSAGES[(offset + index) % len(URGE_MESSAGES)]}，原因是{reason}{URGE_SUFFIXES[(offset + index + (1 if split == 'val' else 0)) % len(URGE_SUFFIXES)]}"
    return make_record(
        bucket="work_order_business_urge",
        split=split,
        index=index,
        source="repo-scenario",
        input_payload=make_input(
            history=object_focus_history(work_order, "work_order", [0, 2, 4, 6][(offset + index) % 4], offset + index // len(WORK_ORDERS)),
            user_message=message,
            runtime=runtime_state("FOCUSED_KNOWLEDGE", {"track": "task", "semantic_kind": "read_only_query"}, {"semantic_kind": "read_only_query"}),
            focused_object=work_order,
        ),
        output_payload={"task": {"commands": [{"command": "start_flow", "flow": "work_order_urge_submission"}, {"command": "set_slots", "slots": {"work_order_id": work_order["id"], "urge_reason": reason}}]}, "knowledge": None, "chitchat": None, "directive": None},
        primary_track="task",
        notes="business urge start with direct reason",
    )


def build_complaint_record(split: str, index: int, offset: int) -> dict:
    work_order = deep_clone(WORK_ORDERS[(offset + index) % len(WORK_ORDERS)])
    reason = COMPLAINT_REASONS[(offset * 2 + index) % len(COMPLAINT_REASONS)]
    prefixes = ["", f"{work_order['title']}这单", "针对当前这条工单，", f"{work_order['id']}这单"]
    message = f"{prefixes[(offset + index + (1 if split == 'val' else 0)) % len(prefixes)]}{COMPLAINT_MESSAGES[(offset + index) % len(COMPLAINT_MESSAGES)]}，主要是因为{reason}{COMPLAINT_SUFFIXES[(offset + index + (1 if split == 'val' else 0)) % len(COMPLAINT_SUFFIXES)]}"
    slots = {"work_order_id": work_order["id"], "complaint_reason": reason}
    if (offset + index) % 3 == 0:
        slots["complaint_confirm"] = "确认"
    return make_record(
        bucket="work_order_business_complaint",
        split=split,
        index=index,
        source="repo-scenario",
        input_payload=make_input(
            history=object_focus_history(work_order, "work_order", [0, 2, 4, 6][(offset + index) % 4], offset + index // len(WORK_ORDERS)),
            user_message=message,
            runtime=runtime_state("FOCUSED_KNOWLEDGE", {"track": "task", "semantic_kind": "read_only_query"}, {"semantic_kind": "read_only_query"}),
            focused_object=work_order,
        ),
        output_payload={"task": {"commands": [{"command": "start_flow", "flow": "complaint_request_submission"}, {"command": "set_slots", "slots": slots}]}, "knowledge": None, "chitchat": None, "directive": None},
        primary_track="task",
        notes="business complaint start with direct reason",
    )


def build_active_slot_fill_record(split: str, index: int, offset: int) -> dict:
    flow_id, step_id, slot_name, message_templates = ACTIVE_SLOT_VARIANTS[(offset + index) % len(ACTIVE_SLOT_VARIANTS)]
    work_order = deep_clone(WORK_ORDERS[(offset + index) % len(WORK_ORDERS)])
    service_item = deep_clone(SERVICE_ITEMS[(offset + index) % len(SERVICE_ITEMS)])
    _, topic_label, _ = RULE_TOPICS[(offset + index) % len(RULE_TOPICS)]
    phone = f"1380000{(offset + index) % 10000:04d}"
    message_override = None
    output_commands = None
    if slot_name == "urge_reason":
        value = URGE_REASONS[(offset + index) % len(URGE_REASONS)]
        message = message_templates[(offset + index) % len(message_templates)].format(reason=value)
        focused_object = work_order
        active_task = task_state(flow_id, step_id, {"work_order_id": work_order["id"]})
        slots = {"urge_reason": value}
    elif slot_name == "complaint_reason":
        value = COMPLAINT_REASONS[(offset + index) % len(COMPLAINT_REASONS)]
        message = message_templates[(offset + index) % len(message_templates)].format(reason=value)
        focused_object = work_order
        active_task = task_state(flow_id, step_id, {"work_order_id": work_order["id"]})
        slots = {"complaint_reason": value}
    elif slot_name == "complaint_confirm":
        negative_confirm = (offset + index) % 4 == 0
        focused_object = work_order
        active_task = task_state(flow_id, step_id, {"work_order_id": work_order["id"], "complaint_reason": COMPLAINT_REASONS[(offset + index) % len(COMPLAINT_REASONS)]})
        if negative_confirm:
            message = COMPLAINT_CANCEL_MESSAGES[(offset + index) % len(COMPLAINT_CANCEL_MESSAGES)]
            slots = {}
            output_commands = [{"command": "cancel_flow"}]
        else:
            value = "确认"
            message = message_templates[(offset + index) % len(message_templates)]
            slots = {"complaint_confirm": value}
    elif slot_name == "contact_phone":
        message = message_templates[(offset + index) % len(message_templates)].format(phone=phone)
        focused_object = work_order
        if flow_id == "work_order_urge_submission":
            active_task = task_state(flow_id, step_id, {"work_order_id": work_order["id"], "urge_reason": URGE_REASONS[(offset + index) % len(URGE_REASONS)]})
        else:
            active_task = task_state(flow_id, step_id, {"work_order_id": work_order["id"], "complaint_reason": COMPLAINT_REASONS[(offset + index) % len(COMPLAINT_REASONS)]})
        slots = {"contact_phone": phone}
    elif slot_name == "rule_topic":
        value = topic_label
        message = message_templates[(offset + index) % len(message_templates)].format(topic_label=topic_label)
        focused_object = None
        active_task = task_state(flow_id, step_id, {})
        slots = {"rule_topic": value}
    else:
        value = service_item["id"]
        message = message_templates[(offset + index) % len(message_templates)].format(service_title=service_item["title"])
        focused_object = service_item
        active_task = task_state(flow_id, step_id, {})
        slots = {"service_item_id": value}
    slot_hints = {
        "urge_reason": "我是在补催办原因",
        "complaint_reason": "这是投诉原因补充",
        "complaint_confirm": "这一轮就是确认提交",
        "contact_phone": "我在补联系电话",
        "rule_topic": "我在补规则主题",
        "service_item_id": "我在确认具体服务项目",
    }
    if split == "val":
        slot_hints = {
            "urge_reason": "这轮是在补催办原因",
            "complaint_reason": "这轮是在补投诉原因",
            "complaint_confirm": "这轮是在确认是否提交",
            "contact_phone": "这轮是在补联系电话",
            "rule_topic": "这轮是在补规则主题",
            "service_item_id": "这轮是在确认具体服务项目",
        }
    message = f"{message}，{slot_hints[slot_name]}"
    if slot_name in {"urge_reason", "complaint_reason"} and (offset + index) % 3 == 0 and flow_id in {"work_order_urge_submission", "complaint_request_submission"}:
        slots["contact_phone"] = f"1380000{(offset + index) % 10000:04d}"
    history = history_from_turns(
        [
            ("继续办理刚才那件事", "可以，我继续沿着当前任务往下走。"),
            ("你现在缺什么信息", f"我现在需要你补充 {slot_name}。"),
            ("别切任务", "好，我先只补当前槽位。"),
        ][: [1, 2, 3][(offset + index) % 3]]
    )
    if output_commands is None:
        output_commands = [{"command": "set_slots", "slots": slots}]
    return make_record(
        bucket="active_task_slot_fill",
        split=split,
        index=index,
        source="repo-scenario" if flow_id in {"work_order_urge_submission", "complaint_request_submission"} else "hand-crafted",
        input_payload=make_input(
            history=history,
            user_message=message,
            runtime=runtime_state("ACTIVE_TASK", {"track": "task", "semantic_kind": "business_task"}, {"semantic_kind": "business_task"}),
            focused_object=focused_object,
            active_task=active_task,
            active_system_task=task_state("system_collect_information", "listen", {"target_slot": slot_name}),
        ),
        output_payload={"task": {"commands": output_commands}, "knowledge": None, "chitchat": None, "directive": None},
        primary_track="task",
        notes=f"active task slot fill for {flow_id}.{slot_name}",
    )


def build_object_followup_record(split: str, index: int, offset: int, intent_sequence: list[str]) -> dict:
    intent = intent_sequence[index]
    history_length = [2, 4, 6][(offset + index) % 3]
    if intent == "work_order_info":
        work_order = deep_clone(WORK_ORDERS[(offset + index) % len(WORK_ORDERS)])
        cycle_seed = offset + index // len(WORK_ORDERS)
        templates = [
            "{title}这条工单是报什么问题来着",
            "把{title}这单的背景再给我概括一下",
            "我想先了解{title}这单本身记录了什么",
            "{title}这单当时登记的情况再顺一遍",
        ]
        message = templates[(cycle_seed + (1 if split == "val" else 0)) % len(templates)].format(title=work_order["title"])
        history = object_focus_history(work_order, "work_order", history_length, cycle_seed)
        focused_object = work_order
    elif intent == "service_item_info":
        service_item = deep_clone(SERVICE_ITEMS[(offset + index) % len(SERVICE_ITEMS)])
        prefix = SERVICE_FOLLOWUP_PREFIXES[(offset + index) % len(SERVICE_FOLLOWUP_PREFIXES)]
        detail = SERVICE_INFO_ASPECTS[(offset + index) % len(SERVICE_INFO_ASPECTS)]
        tail = "，顺着当前项目讲清楚" if split == "val" else "，最好按当前项目来讲"
        message = f"{prefix}{service_item['title']}的{detail}再详细一点{tail}"
        history = object_focus_history(service_item, "service_item", history_length, offset + index // len(SERVICE_ITEMS))
        focused_object = service_item
    else:
        topic_map = {topic_intent: (topic_label, default_question) for topic_intent, topic_label, default_question in RULE_TOPICS}
        topic_label, default_question = topic_map[intent]
        if intent == "general_property_info":
            seed = offset + index * 5
            tail = "，顺着你刚才那个整体问题讲" if split == "val" else "，按整体能力来讲"
            message = f"刚才你提到物业服务，{GENERAL_PROPERTY_MESSAGES[(seed // 2) % len(GENERAL_PROPERTY_MESSAGES)]}{tail}"
        else:
            seed = offset + index * 5
            lead_ins = ["", "顺着刚才的知识问答，", "我这轮还是继续咨询，", "围绕这个规则本身，"]
            tail = "，也把依据讲出来" if split == "val" else "，别只给结论"
            message = f"{lead_ins[(seed + (1 if split == 'val' else 0)) % len(lead_ins)]}{RULE_FOLLOWUP_TEMPLATES[(seed // 2) % len(RULE_FOLLOWUP_TEMPLATES)].format(topic_label=topic_label)}{tail}"
        history = general_history("knowledge", history_length, offset + index, variant=offset + index)
        focused_object = None
    return make_record(
        bucket="object_context_followup",
        split=split,
        index=index,
        source="repo-scenario" if focused_object is not None else "hand-crafted",
        input_payload=make_input(
            history=history,
            user_message=message,
            runtime=runtime_state("FOCUSED_KNOWLEDGE" if focused_object else "IDLE", {"track": "knowledge", "semantic_kind": "knowledge"}, None),
            focused_object=focused_object,
        ),
        output_payload={"task": None, "knowledge": {"intents": [intent]}, "chitchat": None, "directive": None},
        primary_track="knowledge",
        notes=f"follow-up knowledge {intent}",
    )


def build_interrupt_resume_cancel_record(split: str, index: int, offset: int) -> dict:
    scenario_kinds = ["resume", "cancel", "switch_to_complaint", "switch_to_urge"]
    scenario_kind = scenario_kinds[(offset + index) % len(scenario_kinds)]
    work_order = deep_clone(WORK_ORDERS[(offset + index) % len(WORK_ORDERS)])
    cycle_seed = offset + index // len(WORK_ORDERS)
    history = history_from_turns(
        [
            (f"我们刚才在处理{work_order['title']}", "好的，我还记着这条任务。"),
            ("你别把上下文丢了", "不会，我先沿当前链路走。"),
            ("如果要切换我会再说", "明白。"),
        ][: [1, 2, 3][(offset + index) % 3]]
    )
    if scenario_kind == "resume":
        resume_messages = [
            f"继续刚才{work_order['title']}那单的催办",
            f"回到{work_order['id']}这单的催办流程",
            f"{work_order['title']}先接着催办，别断开",
            f"刚才停住的{work_order['title']}催办继续走",
        ]
        user_message = resume_messages[(cycle_seed + (1 if split == "val" else 0)) % len(resume_messages)]
        if split == "val":
            user_message = f"{user_message}，从刚才停住的位置接着办"
        return make_record(
            bucket="task_interrupt_resume_cancel",
            split=split,
            index=index,
            source="hand-crafted",
            input_payload=make_input(
                history=history,
                user_message=user_message,
                runtime=runtime_state("IDLE", {"track": "task", "semantic_kind": "business_task"}, {"semantic_kind": "business_task"}),
                focused_object=work_order,
                paused_tasks=[task_state("work_order_urge_submission", "collect_urge_reason", {"work_order_id": work_order["id"]})],
            ),
            output_payload={"task": {"commands": [{"command": "resume_flow", "flow": "work_order_urge_submission"}]}, "knowledge": None, "chitchat": None, "directive": None},
            primary_track="task",
            notes="resume paused urge flow",
        )
    if scenario_kind == "cancel":
        cancel_messages = [
            f"{work_order['title']}这条投诉先取消",
            f"当前围绕{work_order['id']}的投诉流程我先撤掉",
            f"{work_order['title']}这单的投诉这次别提了",
            f"把{work_order['title']}当前这条投诉先停掉",
        ]
        return make_record(
            bucket="task_interrupt_resume_cancel",
            split=split,
            index=index,
            source="hand-crafted",
            input_payload=make_input(
                history=history,
                user_message=cancel_messages[(cycle_seed + (1 if split == "val" else 0)) % len(cancel_messages)],
                runtime=runtime_state("ACTIVE_TASK", {"track": "task", "semantic_kind": "business_task"}, {"semantic_kind": "business_task"}),
                focused_object=work_order,
                active_task=task_state("complaint_request_submission", "collect_complaint_confirm", {"work_order_id": work_order["id"], "complaint_reason": COMPLAINT_REASONS[(offset + index) % len(COMPLAINT_REASONS)]}),
            ),
            output_payload={"task": {"commands": [{"command": "cancel_flow"}]}, "knowledge": None, "chitchat": None, "directive": None},
            primary_track="task",
            notes="cancel current complaint flow",
        )
    if scenario_kind == "switch_to_complaint":
        switch_reason = COMPLAINT_REASONS[(offset + index) % len(COMPLAINT_REASONS)]
        switch_messages = [
            f"{work_order['title']}这单别只催办了，我要改成投诉，原因是{switch_reason}",
            f"当前这条{work_order['title']}催办先停，我改走投诉，因为{switch_reason}",
            f"{work_order['id']}这单我现在不想只催办，直接投诉，主要是{switch_reason}",
            f"围绕{work_order['title']}，先从催办切到投诉，原因就是{switch_reason}",
        ]
        return make_record(
            bucket="task_interrupt_resume_cancel",
            split=split,
            index=index,
            source="repo-scenario",
            input_payload=make_input(
                history=history,
                user_message=switch_messages[(cycle_seed + (1 if split == "val" else 0)) % len(switch_messages)],
                runtime=runtime_state("ACTIVE_TASK", {"track": "task", "semantic_kind": "business_task"}, {"semantic_kind": "business_task"}),
                focused_object=work_order,
                active_task=task_state("work_order_urge_submission", "collect_urge_reason", {"work_order_id": work_order["id"]}),
            ),
            output_payload={"task": {"commands": [{"command": "start_flow", "flow": "complaint_request_submission"}, {"command": "set_slots", "slots": {"work_order_id": work_order["id"], "complaint_reason": switch_reason}}]}, "knowledge": None, "chitchat": None, "directive": None},
            primary_track="task",
            notes="switch from urge to complaint",
        )
    urge_reason = URGE_REASONS[(offset + index) % len(URGE_REASONS)]
    switch_messages = [
        f"{work_order['title']}这单先不投诉了，改成催办，原因是{urge_reason}",
        f"围绕{work_order['id']}这条，我现在更想催办，因为{urge_reason}",
        f"{work_order['title']}投诉先放下，先催办，主要是{urge_reason}",
        f"把{work_order['title']}从投诉切回催办吧，理由是{urge_reason}",
    ]
    return make_record(
        bucket="task_interrupt_resume_cancel",
        split=split,
        index=index,
        source="repo-scenario",
        input_payload=make_input(
            history=history,
            user_message=switch_messages[(cycle_seed + (1 if split == "val" else 0)) % len(switch_messages)],
            runtime=runtime_state("ACTIVE_TASK", {"track": "task", "semantic_kind": "business_task"}, {"semantic_kind": "business_task"}),
            focused_object=work_order,
            active_task=task_state("complaint_request_submission", "collect_complaint_reason", {"work_order_id": work_order["id"]}),
        ),
        output_payload={"task": {"commands": [{"command": "start_flow", "flow": "work_order_urge_submission"}, {"command": "set_slots", "slots": {"work_order_id": work_order["id"], "urge_reason": urge_reason}}]}, "knowledge": None, "chitchat": None, "directive": None},
        primary_track="task",
        notes="switch from complaint to urge",
    )


def build_split_records(split: str, bucket_specs: dict[str, dict[str, int]]) -> list[dict]:
    offset = 0 if split == "train" else 1000
    service_knowledge_quota = {
        "train": {"service_item_info": 10, "property_fee_rule": 8, "renovation_filing_rule": 8, "parking_rule": 8, "pet_rule": 7, "community_rule": 7, "general_property_info": 7},
        "val": {"service_item_info": 2, "property_fee_rule": 2, "renovation_filing_rule": 2, "parking_rule": 1, "pet_rule": 1, "community_rule": 1, "general_property_info": 1},
    }[split]
    object_followup_quota = {
        "train": {"work_order_info": 20, "service_item_info": 10, "property_fee_rule": 2, "renovation_filing_rule": 2, "parking_rule": 2, "pet_rule": 3, "community_rule": 3, "general_property_info": 3},
        "val": {"work_order_info": 4, "service_item_info": 3},
    }[split]
    read_only_flow_quota = {
        "train": {
            "work_order_status_query": 15,
            "service_progress_tracking": 14,
            "service_item_detail_query": 14,
            "resident_work_orders_list_query": 14,
            "resident_service_items_list_query": 14,
            "resident_rule_qa": 14,
        },
        "val": {
            "work_order_status_query": 3,
            "service_progress_tracking": 3,
            "service_item_detail_query": 3,
            "resident_work_orders_list_query": 3,
            "resident_service_items_list_query": 2,
            "resident_rule_qa": 2,
        },
    }[split]
    read_only_flow_sequence = expand_quota_map(read_only_flow_quota)
    builders = {
        "chitchat": lambda i: build_chitchat_record(split, i, offset),
        "directive_exit_runtime": lambda i: build_directive_record(split, i, offset),
        "ambiguous_all_null": lambda i: build_ambiguous_record(split, i, offset),
        "service_item_knowledge": lambda i: build_service_item_knowledge_record(split, i, offset, expand_quota_map(service_knowledge_quota)),
        "work_order_read_only_task": lambda i: build_read_only_task_record(split, i, offset, read_only_flow_sequence),
        "work_order_business_urge": lambda i: build_urge_record(split, i, offset),
        "work_order_business_complaint": lambda i: build_complaint_record(split, i, offset),
        "active_task_slot_fill": lambda i: build_active_slot_fill_record(split, i, offset),
        "object_context_followup": lambda i: build_object_followup_record(split, i, offset, expand_quota_map(object_followup_quota)),
        "task_interrupt_resume_cancel": lambda i: build_interrupt_resume_cancel_record(split, i, offset),
    }
    records = []
    for bucket, specs in bucket_specs.items():
        for index in range(specs[split]):
            records.append(builders[bucket](index))
    return records


def signature_for_record(record: dict) -> str:
    return json.dumps({"input": record["input"], "output": record["output"]}, ensure_ascii=False, sort_keys=True)
