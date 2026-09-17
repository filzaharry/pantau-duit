import uuid
from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, Text, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin


class TelegramBot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "telegram_bots"

    bot_username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    encrypted_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    webhook_secret: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE')", name="chk_telegram_bots_status"),
    )


class TelegramAccount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "telegram_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    auth_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("idx_telegram_accounts_user", "user_id"),
        Index("idx_telegram_accounts_tg_id", "telegram_user_id"),
    )

    user: Mapped["User"] = relationship("User", back_populates="telegram_accounts")
    chats: Mapped[List["TelegramChat"]] = relationship("TelegramChat", back_populates="telegram_account", cascade="all, delete-orphan")


class TelegramChat(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "telegram_chats"

    telegram_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("telegram_accounts.id", ondelete="CASCADE"), nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    chat_type: Mapped[str] = mapped_column(String(20), default="PRIVATE", nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_state: Mapped[str] = mapped_column(String(50), default="IDLE", nullable=False)
    state_context: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("chat_type IN ('PRIVATE', 'GROUP', 'SUPERGROUP')", name="chk_telegram_chats_type"),
        UniqueConstraint("telegram_account_id", "chat_id", name="uq_telegram_chats_account_chat"),
        Index("idx_telegram_chats_tenant", "tenant_id"),
    )

    telegram_account: Mapped["TelegramAccount"] = relationship("TelegramAccount", back_populates="chats")
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="telegram_chats")
    messages: Mapped[List["TelegramMessage"]] = relationship("TelegramMessage", back_populates="chat", cascade="all, delete-orphan")


class TelegramMessage(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "telegram_messages"

    telegram_chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("telegram_chats.id", ondelete="CASCADE"), nullable=False)
    telegram_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="RECEIVED", nullable=False)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        CheckConstraint("direction IN ('INCOMING', 'OUTGOING')", name="chk_telegram_msg_direction"),
        CheckConstraint(
            "status IN ('RECEIVED', 'PARSED', 'PROCESSED', 'FAILED', 'REPLIED')",
            name="chk_telegram_msg_status"
        ),
        Index("idx_telegram_messages_chat_created", "telegram_chat_id", "created_at"),
    )

    chat: Mapped["TelegramChat"] = relationship("TelegramChat", back_populates="messages")
