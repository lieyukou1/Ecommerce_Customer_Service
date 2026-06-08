from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any


class WorkOrderSummaryData(BaseModel):
    work_order_id: str
    title: str
    category: str
    status: str
    amount: Decimal
    created_at: datetime
    appointment_time: datetime | None = None
    cover_url: str | None = None
    summary: str | None = None


class ServiceItemSummaryData(BaseModel):
    service_item_id: str
    title: str
    price: Decimal
    service_status: str
    cover_url: str | None = None
    description: str | None = None


class ResidentWorkOrdersData(BaseModel):
    resident_id: str
    work_orders: list[WorkOrderSummaryData]


class ResidentServiceItemsData(BaseModel):
    resident_id: str
    service_items: list[ServiceItemSummaryData]


class WorkOrderDetailData(BaseModel):
    work_order_id: str
    title: str
    category: str
    status: str
    status_desc: str
    amount: Decimal
    priority: str
    created_at: datetime
    appointment_time: datetime | None = None
    service_address: str
    contact_name: str
    contact_phone_masked: str


class WorkOrderStatusData(BaseModel):
    work_order_id: str
    status: str
    status_desc: str
    priority: str


class ServiceProgressTraceData(BaseModel):
    time: datetime
    desc: str


class ServiceProgressData(BaseModel):
    work_order_id: str
    service_team: str
    assignee_name: str
    assignee_phone_masked: str
    current_stage: str
    stage_desc: str
    traces: list[ServiceProgressTraceData]


class ServiceItemData(BaseModel):
    service_item_id: str
    title: str
    description: str
    price: Decimal
    service_status: str
    cover_url: str | None = None
    attributes: dict[str, Any]


class OperationResultData(BaseModel):
    request_type: str
    request_id: str
    work_order_id: str
    status: str
    status_desc: str


class WorkOrderUrgeRequestBody(BaseModel):
    submitted_by: str = Field(default="resident")
    reason: str = Field(default="希望物业尽快处理当前工单")


class ComplaintRequestBody(BaseModel):
    submitted_by: str = Field(default="resident")
    reason: str


class ChatObjectPayload(BaseModel):
    type: Literal["work_order", "service_item"]
    id: str
    title: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    sender_id: str
    text: str | None = None
    object: ChatObjectPayload | None = None


class ChatMessage(BaseModel):
    role: Literal["user", "bot", "divider"]
    text: str | None = None
    object: ChatObjectPayload | None = None
    suggestions: list[str] | None = None


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    messages: list[ChatMessage]
