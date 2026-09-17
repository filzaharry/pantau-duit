import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Any
from sqlalchemy import String, BigInteger, Boolean, DateTime, Text, Numeric, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class AlertRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "alert_rules"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    threshold_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    channels: Mapped[list[str]] = mapped_column(JSONB, default=["TELEGRAM", "DASHBOARD"], nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "rule_type IN ('LOW_BALANCE', 'BUDGET_THRESHOLD', 'BUDGET_EXCEEDED', 'SUBSCRIPTION_EXPIRY', 'PAYMENT_REMINDER', 'RECURRING_REMINDER', 'UNUSUAL_SPENDING', 'GOAL_MILESTONE')",
            name="chk_alert_rules_type"
        ),
        Index("idx_alert_rules_tenant", "tenant_id"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="alert_rules")


class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "notifications"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    data_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("channel IN ('TELEGRAM', 'EMAIL', 'DASHBOARD')", name="chk_notifications_channel"),
        CheckConstraint("status IN ('PENDING', 'SENT', 'FAILED', 'READ')", name="chk_notifications_status"),
        Index("idx_notifications_user_status", "user_id", "status", "created_at"),
    )

    user: Mapped["User"] = relationship("User", back_populates="notifications")


class NotificationPreference(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("channel IN ('TELEGRAM', 'EMAIL', 'DASHBOARD')", name="chk_notif_pref_channel"),
        UniqueConstraint("user_id", "channel", "notification_type", name="uq_notif_pref_user_channel_type"),
    )


class UsageRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "usage_records"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    metric: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # 'YYYY-MM'
    count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    __table_args__ = (
        CheckConstraint("count >= 0", name="chk_usage_records_count"),
        UniqueConstraint("tenant_id", "metric", "period", name="uq_usage_records_tenant_metric_period"),
        Index("idx_usage_records_tenant_period", "tenant_id", "period"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="usage_records")


class AuditLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "audit_logs"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(20), default="USER", nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "actor_type IN ('USER', 'SYSTEM', 'SUPERADMIN', 'TELEGRAM_BOT')",
            name="chk_audit_logs_actor_type"
        ),
        Index("idx_audit_logs_tenant_created", "tenant_id", "created_at"),
        Index("idx_audit_logs_actor_created", "actor_id", "created_at"),
        Index("idx_audit_logs_entity", "entity_type", "entity_id"),
    )

    tenant: Mapped[Optional["Tenant"]] = relationship("Tenant", back_populates="audit_logs")
    actor: Mapped[Optional["User"]] = relationship("User")
