import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Any
from sqlalchemy import String, Integer, Boolean, DateTime, Date, Text, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class Account(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "accounts"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    account_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="IDR", nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "type IN ('BANK', 'CASH', 'E_WALLET', 'CREDIT_CARD', 'INVESTMENT', 'OTHER')",
            name="chk_accounts_type"
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'ARCHIVED', 'CLOSED')",
            name="chk_accounts_status"
        ),
        Index("idx_accounts_tenant_status", "tenant_id", "status"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="[Transaction.account_id]",
        back_populates="account"
    )
    inbound_transfers: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="[Transaction.destination_account_id]",
        back_populates="destination_account"
    )


class Category(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "categories"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "type IN ('EXPENSE', 'INCOME', 'INVESTMENT', 'BOTH')",
            name="chk_categories_type"
        ),
        Index("idx_categories_tenant_type", "tenant_id", "type"),
        Index("idx_categories_slug", "slug"),
    )

    tenant: Mapped[Optional["Tenant"]] = relationship("Tenant", back_populates="categories")
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side="[Category.id]", back_populates="subcategories")
    subcategories: Mapped[List["Category"]] = relationship("Category", back_populates="parent")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="category")


class Transaction(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "transactions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    destination_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(20), default="DASHBOARD", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="COMPLETED", nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    recurring_transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, default=dict, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_transactions_amount"),
        CheckConstraint(
            "transaction_type IN ('EXPENSE', 'INCOME', 'INVESTMENT', 'TRANSFER', 'REFUND')",
            name="chk_transactions_type"
        ),
        CheckConstraint(
            "source IN ('TELEGRAM', 'DASHBOARD', 'SYSTEM', 'API')",
            name="chk_transactions_source"
        ),
        CheckConstraint(
            "status IN ('COMPLETED', 'PENDING', 'VOIDED', 'DRAFT')",
            name="chk_transactions_status"
        ),
        # Hot-path composite index for user feed & timeline
        Index("idx_transactions_feed", "tenant_id", "transaction_date"),
        # Critical composite index for dashboard analytics aggregation
        Index("idx_transactions_aggregation", "tenant_id", "transaction_type", "status", "transaction_date"),
        # Category breakdown index
        Index("idx_transactions_category_date", "tenant_id", "category_id", "transaction_date"),
        # Account ledger history index
        Index("idx_transactions_account_date", "tenant_id", "account_id", "transaction_date"),
        # Transfer destination lookup
        Index("idx_transactions_dest_account", "destination_account_id"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="transactions")
    account: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], back_populates="transactions")
    destination_account: Mapped[Optional["Account"]] = relationship("Account", foreign_keys=[destination_account_id], back_populates="inbound_transfers")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="transactions")
    creator: Mapped[Optional["User"]] = relationship("User")


class Budget(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "budgets"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    period: Mapped[str] = mapped_column(String(20), default="MONTHLY", nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    alert_threshold_percent: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_budgets_amount"),
        CheckConstraint("end_date >= start_date", name="chk_budgets_dates"),
        CheckConstraint("alert_threshold_percent BETWEEN 1 AND 100", name="chk_budgets_threshold"),
        CheckConstraint("period IN ('WEEKLY', 'MONTHLY', 'YEARLY', 'CUSTOM')", name="chk_budgets_period"),
        Index("idx_budgets_tenant_active", "tenant_id", "is_active", "start_date", "end_date"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="budgets")
    category: Mapped[Optional["Category"]] = relationship("Category")


class FinancialGoal(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "financial_goals"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="IN_PROGRESS", nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        CheckConstraint("target_amount > 0", name="chk_financial_goals_target"),
        CheckConstraint("current_amount >= 0", name="chk_financial_goals_current"),
        CheckConstraint("status IN ('IN_PROGRESS', 'REACHED', 'PAUSED', 'CANCELLED')", name="chk_financial_goals_status"),
        Index("idx_financial_goals_tenant_status", "tenant_id", "status"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="financial_goals")
    contributions: Mapped[List["GoalContribution"]] = relationship("GoalContribution", back_populates="goal", cascade="all, delete-orphan")


class GoalContribution(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "goal_contributions"

    goal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("financial_goals.id", ondelete="CASCADE"), nullable=False)
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    contribution_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_goal_contributions_amount"),
        Index("idx_goal_contributions_goal", "goal_id"),
    )

    goal: Mapped["FinancialGoal"] = relationship("FinancialGoal", back_populates="contributions")
    transaction: Mapped[Optional["Transaction"]] = relationship("Transaction")


class RecurringTransaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "recurring_transactions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    destination_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    cron_expression: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_execution_date: Mapped[date] = mapped_column(Date, nullable=False)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_recurring_transactions_amount"),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="chk_recurring_dates"),
        CheckConstraint("transaction_type IN ('EXPENSE', 'INCOME', 'TRANSFER')", name="chk_recurring_type"),
        CheckConstraint("frequency IN ('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', 'CUSTOM')", name="chk_recurring_frequency"),
        CheckConstraint("status IN ('ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED')", name="chk_recurring_status"),
        Index("idx_recurring_tenant_status", "tenant_id", "status"),
        Index("idx_recurring_next_exec", "status", "next_execution_date"),
    )

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="recurring_transactions")
    account: Mapped["Account"] = relationship("Account", foreign_keys=[account_id])
    destination_account: Mapped[Optional["Account"]] = relationship("Account", foreign_keys=[destination_account_id])
    category: Mapped[Optional["Category"]] = relationship("Category")
