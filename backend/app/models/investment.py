import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, DateTime, Text, Numeric, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class InvestmentAsset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "investment_assets"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(30), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="IDR", nullable=False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0.0000"), nullable=False)
    last_price_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "asset_type IN ('STOCK', 'CRYPTO', 'MUTUAL_FUND', 'BOND', 'COMMODITY', 'REAL_ESTATE', 'OTHER')",
            name="chk_investment_assets_type"
        ),
        Index("idx_investment_assets_symbol", "symbol"),
    )


class InvestmentHolding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "investment_holdings"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("investment_assets.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("0.00000000"), nullable=False)
    average_buy_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0.0000"), nullable=False)

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="chk_investment_holdings_quantity"),
        UniqueConstraint("tenant_id", "account_id", "asset_id", name="uq_investment_holdings_tenant_account_asset"),
        Index("idx_investment_holdings_tenant", "tenant_id"),
    )

    account: Mapped["Account"] = relationship("Account")
    asset: Mapped["InvestmentAsset"] = relationship("InvestmentAsset")


class InvestmentTransaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "investment_transactions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False)
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("investment_assets.id", ondelete="RESTRICT"), nullable=False)
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "type IN ('BUY', 'SELL', 'DIVIDEND', 'DEPOSIT', 'WITHDRAW', 'FEE')",
            name="chk_investment_tx_type"
        ),
        Index("idx_investment_tx_tenant_date", "tenant_id", "transaction_date"),
    )

    account: Mapped["Account"] = relationship("Account")
    asset: Mapped["InvestmentAsset"] = relationship("InvestmentAsset")
    transaction: Mapped[Optional["Transaction"]] = relationship("Transaction")
