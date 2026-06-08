from __future__ import annotations


def normalize_rule_topic(topic: str) -> str:
    """
    功能：把住户规则主题归一化到系统支持的 topic key。

    输入：
    - topic: 原始规则主题文本。

    输出：
    - str: 识别出的规则 topic key；无法识别时返回空字符串。

    调用情况：
    - `AnswerResidentRule.run()`
    - `build_rule_answer()`

    副作用：
    - 无。
    """
    normalized = (topic or "").strip().lower()

    topic_rules = {
        "property_fee": ("物业费", "物管费", "缴费", "收费"),
        "renovation": ("装修", "报备", "施工", "装修证"),
        "parking": ("停车", "车位", "临停", "月卡"),
        "pet": ("宠物", "养狗", "遛狗", "猫"),
        "visitor": ("访客", "来访", "门禁", "登记"),
        "public_facility": ("公共区域", "公共设施", "电梯", "楼道"),
    }

    if normalized in topic_rules:
        return normalized

    for topic_key, keywords in topic_rules.items():
        if any(keyword in normalized for keyword in keywords):
            return topic_key

    return ""


def build_rule_answer(topic: str) -> str:
    """
    功能：根据规则主题生成住户规则答复。

    输入：
    - topic: 原始规则主题文本。

    输出：
    - str: 匹配主题后的规则说明文案。

    调用情况：
    - `AnswerResidentRule.run()`

    副作用：
    - 无。
    """
    topic_key = normalize_rule_topic(topic)

    answers = {
        "property_fee": (
            "物业费通常按小区公示口径按期缴纳。具体收费标准、优惠周期和补缴规则，"
            "以你所在小区的收费通知和物业服务合同为准。"
        ),
        "renovation": (
            "装修类事项一般需要先做装修报备，再按要求提交施工时间、施工人员和材料信息。"
            "是否收取保证金、施工时段限制和垃圾清运要求，以小区装修管理规定为准。"
        ),
        "parking": (
            "停车规则通常会区分固定车位、临停和访客停车。收费标准、放行方式和夜间管理要求，"
            "以小区停车管理通知和现场标识为准。"
        ),
        "pet": (
            "宠物管理通常会要求文明牵引、及时清理和遵守公共区域管理要求。"
            "是否需要登记、禁养范围和重点区域限制，以小区公约和物业通知为准。"
        ),
        "visitor": (
            "访客通行一般需要按门禁或访客登记流程办理。"
            "具体可通行时段、车辆放行和身份核验要求，以小区门岗制度为准。"
        ),
        "public_facility": (
            "公共设施使用通常会区分预约、开放时段和安全责任。"
            "电梯、楼道、公共活动区等具体规则，以现场公示和物业通知为准。"
        ),
    }

    return answers.get(
        topic_key,
        "这类物业规则我可以先给你常见办理口径，但最终仍要以小区公示、物业通知和现场执行标准为准。"
        "如果你告诉我更具体的主题，比如物业费、装修报备、停车规则或宠物管理，我可以再说得更聚焦一些。",
    )
