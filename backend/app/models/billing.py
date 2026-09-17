import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Any
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Numeric, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class Plan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plans"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="IDR", nullable=False)
    interval: Mapped[str] = mapped_column(String(20), default="MONTHLY", nullable=False)
    interval_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    trial_period_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_plans_price"),
        CheckConstraint("interval IN ('MONTHLY', 'YEARLY', 'LIFETIME')", name="chk_plans_interval"),
    )

    features: Mapped[List["PlanFeature"]] = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="plan")


class PlanFeature(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plan_features"

    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    feature_key: Mapped[str] = mapped_column(String(100), nullable=False)
    feature_value: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint("plan_id", "feature_key", name="uq_plan_features_plan_key"),
        Index("idx_plan_features_key", "feature_key"),
    )

    plan: Mapped["Plan"] = relationship("Plan", back_populates="features")


class Subscription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    grace_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, default=dict, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'ACTIVE', 'GRACE_PERIOD', 'EXPIRED', 'CANCELLED', 'SUSPENDED')",
            name="chk_subscriptions_status"
        ),
        CheckConstraint(
            "current_period_end >= current_period_start",
            name="chk_subscriptions_period"
        ),
        CheckConstraint(
            "grace_period_end IS NULL OR grace_period_end >= current_period_end",
            name="chk_subscriptions_grace_period"
        ),
        Index("idx_subscriptions_tenant_status", "tenant_id", "status"),
        Index("idx_subscriptions_status_end", "status", "current_period_end"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship("Plan", back_populates="subscriptions")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="subscription")


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payments"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False)
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="RESTRICT"), nullable=True)
    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    external_payment_id: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="IDR", nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_channel: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, default=dict, nullable=True)

    __table_args__ = (
        CheckConstraint("amount >= 0", name="chk_payments_amount"),
        CheckConstraint(
            "status IN ('PENDING', 'PAID', 'FAILED', 'EXPIRED', 'REFUNDED')",
            name="chk_payments_status"
        ),
        Index("idx_payments_tenant_created", "tenant_id", "created_at"),
        Index("idx_payments_status_created", "status", "created_at"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="payments")
    subscription: Mapped[Optional["Subscription"]] = relationship("Subscription", back_populates="payments")
    events: Mapped[List["PaymentEvent"]] = relationship("PaymentEvent", back_populates="payment")


class PaymentEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "payment_events"

    payment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    external_event_id: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="RECEIVED", nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('RECEIVED', 'PROCESSED', 'FAILED', 'IGNORED')",
            name="chk_payment_events_status"
        ),
        Index("idx_payment_events_payment", "payment_id"),
        Index("idx_payment_events_type_status", "event_type", "status"),
    )

    payment: Mapped[Optional["Payment"]] = relationship("Payment", back_populates="events")
