import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class Tenant(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), default="PERSONAL", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="IDR", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Jakarta", nullable=False)

    __table_args__ = (
        CheckConstraint(
            "type IN ('PERSONAL', 'FAMILY', 'BUSINESS')",
            name="chk_tenants_type"
        ),
        Index("idx_tenants_slug", "slug"),
    )

    # Relationships
    members: Mapped[List["TenantUser"]] = relationship("TenantUser", back_populates="tenant", cascade="all, delete-orphan")
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="tenant")
    categories: Mapped[List["Category"]] = relationship("Category", back_populates="tenant", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="tenant")
    budgets: Mapped[List["Budget"]] = relationship("Budget", back_populates="tenant", cascade="all, delete-orphan")
    financial_goals: Mapped[List["FinancialGoal"]] = relationship("FinancialGoal", back_populates="tenant", cascade="all, delete-orphan")
    recurring_transactions: Mapped[List["RecurringTransaction"]] = relationship("RecurringTransaction", back_populates="tenant", cascade="all, delete-orphan")
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="tenant")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="tenant")
    usage_records: Mapped[List["UsageRecord"]] = relationship("UsageRecord", back_populates="tenant", cascade="all, delete-orphan")
    telegram_chats: Mapped[List["TelegramChat"]] = relationship("TelegramChat", back_populates="tenant")
    alert_rules: Mapped[List["AlertRule"]] = relationship("AlertRule", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="tenant")
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="tenant", cascade="all, delete-orphan")
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="tenant", cascade="all, delete-orphan")
    payroll_runs: Mapped[List["PayrollRun"]] = relationship("PayrollRun", back_populates="tenant", cascade="all, delete-orphan")
    leave_requests: Mapped[List["LeaveRequest"]] = relationship("LeaveRequest", back_populates="tenant", cascade="all, delete-orphan")
    reimbursements: Mapped[List["Reimbursement"]] = relationship("Reimbursement", back_populates="tenant", cascade="all, delete-orphan")
    shifts: Mapped[List["Shift"]] = relationship("Shift", back_populates="tenant", cascade="all, delete-orphan")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="tenant", cascade="all, delete-orphan")
    overtime_requests: Mapped[List["OvertimeRequest"]] = relationship("OvertimeRequest", back_populates="tenant", cascade="all, delete-orphan")
    fingerprint_devices: Mapped[List["FingerprintDevice"]] = relationship("FingerprintDevice", back_populates="tenant", cascade="all, delete-orphan")
    document_templates: Mapped[List["DocumentTemplate"]] = relationship("DocumentTemplate", back_populates="tenant", cascade="all, delete-orphan")
    employee_documents: Mapped[List["EmployeeDocument"]] = relationship("EmployeeDocument", back_populates="tenant", cascade="all, delete-orphan")


class TenantUser(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tenant_users"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('INVITED', 'ACTIVE', 'SUSPENDED', 'REMOVED')",
            name="chk_tenant_users_status"
        ),
        UniqueConstraint("tenant_id", "user_id", name="uq_tenant_users_tenant_user"),
        Index("idx_tenant_users_user", "user_id"),
        Index("idx_tenant_users_tenant", "tenant_id"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="tenant_memberships")
    roles: Mapped[List["TenantUserRole"]] = relationship("TenantUserRole", back_populates="tenant_user", cascade="all, delete-orphan")
