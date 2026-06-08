from enum import Enum


class SemanticKind(str, Enum):
    RUNTIME_CONTROL = "runtime_control"
    READ_ONLY_QUERY = "read_only_query"
    BUSINESS_TASK = "business_task"
    SOCIAL_OR_CLARIFY = "social_or_clarify"
