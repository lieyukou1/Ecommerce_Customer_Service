from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    ComplaintRequest,
    Resident,
    ResidentServiceItem,
    ServiceItem,
    ServiceProgressRecord,
    ServiceProgressTrace,
    WorkOrder,
    WorkOrderUrgeRequest,
)
from app.schemas import (
    ApiResponse,
    ChatHistoryResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ComplaintRequestBody,
    OperationResultData,
    ResidentServiceItemsData,
    ResidentWorkOrdersData,
    ServiceItemData,
    ServiceItemSummaryData,
    ServiceProgressData,
    ServiceProgressTraceData,
    WorkOrderDetailData,
    WorkOrderStatusData,
    WorkOrderSummaryData,
    WorkOrderUrgeRequestBody,
)


router = APIRouter()


def _wrap(data):
    return ApiResponse(data=data)


def _get_resident_or_404(db: Session, resident_id: str) -> Resident:
    resident = db.query(Resident).filter(Resident.resident_id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail=f"住户 {resident_id} 不存在。")
    return resident


def _get_work_order_or_404(db: Session, work_order_id: str) -> WorkOrder:
    work_order = (
        db.query(WorkOrder)
        .options(
            joinedload(WorkOrder.resident),
            joinedload(WorkOrder.progress_records).joinedload(ServiceProgressRecord.traces),
            joinedload(WorkOrder.complaint_requests),
            joinedload(WorkOrder.urge_requests),
        )
        .filter(WorkOrder.work_order_id == work_order_id)
        .first()
    )
    if not work_order:
        raise HTTPException(status_code=404, detail=f"工单 {work_order_id} 不存在。")
    return work_order


def _get_service_item_or_404(db: Session, service_item_id: str) -> ServiceItem:
    service_item = db.query(ServiceItem).filter(ServiceItem.service_item_id == service_item_id).first()
    if not service_item:
        raise HTTPException(status_code=404, detail=f"服务项目 {service_item_id} 不存在。")
    return service_item


def _build_resident_work_orders(db: Session, resident: Resident) -> list[WorkOrderSummaryData]:
    work_orders = (
        db.query(WorkOrder)
        .filter(WorkOrder.resident_id == resident.id)
        .order_by(WorkOrder.created_at.desc())
        .all()
    )
    return [
        WorkOrderSummaryData(
            work_order_id=work_order.work_order_id,
            title=work_order.title,
            category=work_order.category,
            status=work_order.status,
            amount=work_order.amount,
            created_at=work_order.created_at,
            appointment_time=work_order.appointment_time,
            cover_url=None,
            summary=work_order.status_desc,
        )
        for work_order in work_orders
    ]


def _build_resident_service_items(db: Session, resident: Resident) -> list[ServiceItemSummaryData]:
    service_links = (
        db.query(ResidentServiceItem)
        .options(joinedload(ResidentServiceItem.service_item))
        .filter(ResidentServiceItem.resident_id == resident.id)
        .order_by(ResidentServiceItem.created_at.desc())
        .all()
    )

    seen: set[str] = set()
    service_items: list[ServiceItemSummaryData] = []
    for link in service_links:
        item = link.service_item
        if not item or item.service_item_id in seen:
            continue
        seen.add(item.service_item_id)
        service_items.append(
            ServiceItemSummaryData(
                service_item_id=item.service_item_id,
                title=item.title,
                price=item.price,
                service_status=item.service_status,
                cover_url=item.cover_url,
                description=item.description,
            )
        )
    return service_items


def _build_history_messages(resident_id: str) -> ChatHistoryResponse:
    return ChatHistoryResponse(
        messages=[
            ChatMessage(
                role="bot",
                text=(
                    f"欢迎进入物业业务演示版，当前住户为 {resident_id}。"
                    " 智能管家能力暂未接入，现在可以先体验工单、服务项目、投诉与催办相关功能。"
                ),
                suggestions=["查看我的工单", "看看服务项目", "装修报备怎么做", "停车规则是什么"],
            ),
            ChatMessage(
                role="divider",
                text="以上为系统预置提示",
            ),
        ]
    )


def _build_placeholder_reply(payload: ChatRequest) -> ChatResponse:
    if payload.object:
        if payload.object.type == "work_order":
            text = (
                f"已收到工单对象：{payload.object.title}。"
                " 当前演示版不会自动分析意图，但你可以继续通过右侧卡片查看工单状态、处理进度、催办和投诉接口。"
            )
            suggestions = ["查询当前工单状态", "查看处理进度", "发起催办", "提交投诉"]
        else:
            text = (
                f"已收到服务项目对象：{payload.object.title}。"
                " 当前演示版保留了对象驱动交互入口，后续可在此接入真实智能管家咨询能力。"
            )
            suggestions = ["这个服务怎么收费", "适用时间是什么", "办理流程是什么"]
    else:
        text = (
            "当前聊天区为物业业务演示占位版，已经保留了交互壳和消息流。"
            " 你现在可以重点体验右侧工单与服务项目数据，以及后端接口返回。"
        )
        suggestions = ["查看我的工单", "看看服务项目", "物业费规则", "宠物管理规定"]

    return ChatResponse(messages=[ChatMessage(role="bot", text=text, suggestions=suggestions)])


@router.get(
    "/health",
    response_model=ApiResponse,
    tags=["系统"],
    summary="物业中台健康检查",
    description="检查物业中台服务和数据库连通性。",
)
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return _wrap({"status": "ok"})


@router.get(
    "/residents/{resident_id}/work-orders",
    response_model=ApiResponse,
    tags=["住户"],
    summary="查询住户工单列表",
    description="按住户编号查询其关联的物业工单列表。",
)
def resident_work_orders(resident_id: str, db: Session = Depends(get_db)):
    resident = _get_resident_or_404(db, resident_id)
    return _wrap(
        ResidentWorkOrdersData(
            resident_id=resident.resident_id,
            work_orders=_build_resident_work_orders(db, resident),
        )
    )


@router.get(
    "/residents/{resident_id}/service-items",
    response_model=ApiResponse,
    tags=["住户"],
    summary="查询住户服务项目列表",
    description="按住户编号查询其常用或关联的物业服务项目。",
)
def resident_service_items(resident_id: str, db: Session = Depends(get_db)):
    resident = _get_resident_or_404(db, resident_id)
    return _wrap(
        ResidentServiceItemsData(
            resident_id=resident.resident_id,
            service_items=_build_resident_service_items(db, resident),
        )
    )


@router.get(
    "/work-orders/{work_order_id}",
    response_model=ApiResponse,
    tags=["工单"],
    summary="查询工单详情",
    description="返回工单主信息、服务地址、预约时间和联系人信息。",
)
def work_order_detail(work_order_id: str, db: Session = Depends(get_db)):
    work_order = _get_work_order_or_404(db, work_order_id)
    return _wrap(
        WorkOrderDetailData(
            work_order_id=work_order.work_order_id,
            title=work_order.title,
            category=work_order.category,
            status=work_order.status,
            status_desc=work_order.status_desc,
            amount=work_order.amount,
            priority=work_order.priority,
            created_at=work_order.created_at,
            appointment_time=work_order.appointment_time,
            service_address=work_order.service_address,
            contact_name=work_order.contact_name,
            contact_phone_masked=work_order.contact_phone_masked,
        )
    )


@router.get(
    "/work-orders/{work_order_id}/status",
    response_model=ApiResponse,
    tags=["工单"],
    summary="查询工单状态",
    description="返回工单当前状态、状态说明和优先级。",
)
def work_order_status(work_order_id: str, db: Session = Depends(get_db)):
    work_order = _get_work_order_or_404(db, work_order_id)
    return _wrap(
        WorkOrderStatusData(
            work_order_id=work_order.work_order_id,
            status=work_order.status,
            status_desc=work_order.status_desc,
            priority=work_order.priority,
        )
    )


@router.get(
    "/work-orders/{work_order_id}/progress",
    response_model=ApiResponse,
    tags=["工单"],
    summary="查询工单处理进度",
    description="返回工单当前处理阶段、责任班组和进度时间线。",
)
def work_order_progress(work_order_id: str, db: Session = Depends(get_db)):
    work_order = _get_work_order_or_404(db, work_order_id)
    record = (
        db.query(ServiceProgressRecord)
        .options(joinedload(ServiceProgressRecord.traces))
        .filter(ServiceProgressRecord.work_order_id == work_order.id)
        .order_by(ServiceProgressRecord.updated_at.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail=f"工单 {work_order_id} 暂无处理进度。")

    traces = sorted(record.traces, key=lambda item: item.trace_time, reverse=True)
    return _wrap(
        ServiceProgressData(
            work_order_id=work_order.work_order_id,
            service_team=record.service_team,
            assignee_name=record.assignee_name,
            assignee_phone_masked=record.assignee_phone_masked,
            current_stage=record.current_stage,
            stage_desc=record.stage_desc,
            traces=[ServiceProgressTraceData(time=trace.trace_time, desc=trace.trace_desc) for trace in traces],
        )
    )


@router.get(
    "/service-items/{service_item_id}",
    response_model=ApiResponse,
    tags=["服务项目"],
    summary="查询服务项目详情",
    description="返回服务项目说明、价格、状态和展示属性。",
)
def service_item_detail(service_item_id: str, db: Session = Depends(get_db)):
    service_item = _get_service_item_or_404(db, service_item_id)
    return _wrap(
        ServiceItemData(
            service_item_id=service_item.service_item_id,
            title=service_item.title,
            description=service_item.description,
            price=service_item.price,
            service_status=service_item.service_status,
            cover_url=service_item.cover_url,
            attributes=service_item.attributes_json or {},
        )
    )


@router.post(
    "/work-orders/{work_order_id}/urge-requests",
    response_model=ApiResponse,
    tags=["工单"],
    summary="提交工单催办",
    description="针对待受理、处理中或待上门工单发起催办请求。",
)
def create_work_order_urge_request(
    work_order_id: str,
    body: WorkOrderUrgeRequestBody,
    db: Session = Depends(get_db),
):
    work_order = _get_work_order_or_404(db, work_order_id)
    if work_order.status not in {"待受理", "处理中", "待上门"}:
        raise HTTPException(
            status_code=400,
            detail=f"工单当前状态为“{work_order.status}”，暂不支持继续催办。",
        )

    operation_id = f"U{datetime.now():%Y%m%d%H%M%S}{uuid4().hex[:6].upper()}"
    urge = WorkOrderUrgeRequest(
        urge_id=operation_id,
        work_order_id=work_order.id,
        submitted_by=body.submitted_by,
        reason=body.reason,
        status="submitted",
        status_desc="催办申请已提交，物业服务中心会尽快跟进。",
        created_at=datetime.now(),
    )
    db.add(urge)
    db.commit()

    return _wrap(
        OperationResultData(
            request_type="work_order_urge_request",
            request_id=operation_id,
            work_order_id=work_order.work_order_id,
            status="submitted",
            status_desc=urge.status_desc,
        )
    )


@router.post(
    "/work-orders/{work_order_id}/complaint-requests",
    response_model=ApiResponse,
    tags=["工单"],
    summary="提交投诉报事",
    description="针对工单处理结果或服务过程发起投诉/异议请求。",
)
def create_complaint_request(
    work_order_id: str,
    body: ComplaintRequestBody,
    db: Session = Depends(get_db),
):
    work_order = _get_work_order_or_404(db, work_order_id)

    existing = (
        db.query(ComplaintRequest)
        .filter(ComplaintRequest.work_order_id == work_order.id)
        .order_by(ComplaintRequest.created_at.desc())
        .first()
    )
    if existing and existing.status in {"submitted", "processing"}:
        raise HTTPException(
            status_code=409,
            detail=f"工单 {work_order_id} 已存在处理中投诉，请勿重复提交。",
        )

    operation_id = f"C{datetime.now():%Y%m%d%H%M%S}{uuid4().hex[:6].upper()}"
    complaint = ComplaintRequest(
        complaint_id=operation_id,
        work_order_id=work_order.id,
        submitted_by=body.submitted_by,
        reason=body.reason,
        status="submitted",
        status_desc="投诉申请已提交，客服管家将在一个工作日内回访。",
        created_at=datetime.now(),
    )
    db.add(complaint)
    db.commit()

    return _wrap(
        OperationResultData(
            request_type="complaint_request",
            request_id=operation_id,
            work_order_id=work_order.work_order_id,
            status="submitted",
            status_desc=complaint.status_desc,
        )
    )


@router.get(
    "/api/chat/history",
    response_model=ChatHistoryResponse,
    tags=["交互壳"],
    summary="获取占位聊天历史",
    description="返回物业演示版的静态欢迎消息，避免前端在未接入智能管家时报错。",
)
def chat_history(sender_id: str):
    return _build_history_messages(sender_id)


@router.post(
    "/api/chat",
    response_model=ChatResponse,
    tags=["交互壳"],
    summary="占位聊天回复",
    description="返回固定提示语，用于保留老师原有交互壳和对象驱动消息流。",
)
def placeholder_chat(payload: ChatRequest):
    return _build_placeholder_reply(payload)
