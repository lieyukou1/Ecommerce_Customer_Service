from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Resident(Base):
    __tablename__ = "residents"

    id: Mapped[int] = mapped_column(primary_key=True)
    resident_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    resident_level: Mapped[str] = mapped_column(String(32))
    mobile_masked: Mapped[str] = mapped_column(String(32))
    building: Mapped[str] = mapped_column(String(64))
    room_no: Mapped[str] = mapped_column(String(64))
    profile_note: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime)

    work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="resident")
    service_items: Mapped[list["ResidentServiceItem"]] = relationship(back_populates="resident")


class ServiceItem(Base):
    __tablename__ = "service_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_item_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    service_status: Mapped[str] = mapped_column(String(32))
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    attributes_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime)

    resident_links: Mapped[list["ResidentServiceItem"]] = relationship(back_populates="service_item")


class ResidentServiceItem(Base):
    __tablename__ = "resident_service_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    resident_id: Mapped[int] = mapped_column(ForeignKey("residents.id"))
    service_item_id: Mapped[int] = mapped_column(ForeignKey("service_items.id"))
    relation_type: Mapped[str] = mapped_column(String(64))
    note: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime)

    resident: Mapped[Resident] = relationship(back_populates="service_items")
    service_item: Mapped[ServiceItem] = relationship(back_populates="resident_links")


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    work_order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    resident_id: Mapped[int] = mapped_column(ForeignKey("residents.id"))
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    status_desc: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    priority: Mapped[str] = mapped_column(String(32))
    service_address: Mapped[str] = mapped_column(String(255))
    contact_name: Mapped[str] = mapped_column(String(64))
    contact_phone_masked: Mapped[str] = mapped_column(String(32))
    appointment_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)

    resident: Mapped[Resident] = relationship(back_populates="work_orders")
    progress_records: Mapped[list["ServiceProgressRecord"]] = relationship(back_populates="work_order")
    complaint_requests: Mapped[list["ComplaintRequest"]] = relationship(back_populates="work_order")
    urge_requests: Mapped[list["WorkOrderUrgeRequest"]] = relationship(back_populates="work_order")


class ServiceProgressRecord(Base):
    __tablename__ = "service_progress_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"))
    service_team: Mapped[str] = mapped_column(String(64))
    assignee_name: Mapped[str] = mapped_column(String(64))
    assignee_phone_masked: Mapped[str] = mapped_column(String(32))
    current_stage: Mapped[str] = mapped_column(String(32))
    stage_desc: Mapped[str] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(DateTime)

    work_order: Mapped[WorkOrder] = relationship(back_populates="progress_records")
    traces: Mapped[list["ServiceProgressTrace"]] = relationship(back_populates="record")


class ServiceProgressTrace(Base):
    __tablename__ = "service_progress_traces"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_progress_record_id: Mapped[int] = mapped_column(ForeignKey("service_progress_records.id"))
    trace_time: Mapped[datetime] = mapped_column(DateTime)
    trace_desc: Mapped[str] = mapped_column(String(255))

    record: Mapped[ServiceProgressRecord] = relationship(back_populates="traces")


class ComplaintRequest(Base):
    __tablename__ = "complaint_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"))
    submitted_by: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))
    status_desc: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime)

    work_order: Mapped[WorkOrder] = relationship(back_populates="complaint_requests")


class WorkOrderUrgeRequest(Base):
    __tablename__ = "work_order_urge_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    urge_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"))
    submitted_by: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32))
    status_desc: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime)

    work_order: Mapped[WorkOrder] = relationship(back_populates="urge_requests")
