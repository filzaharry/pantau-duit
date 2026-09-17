import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'SUSPENDED', 'DELETED')",
            name="chk_users_status"
        ),
        Index("idx_users_email", "email"),
        Index("idx_users_status", "status"),
    )

    # Relationships
    sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    verifications: Mapped[List["AuthVerification"]] = relationship("AuthVerification", back_populates="user", cascade="all, delete-orphan")
    tenant_memberships: Mapped[List["TenantUser"]] = relationship("TenantUser", back_populates="user", cascade="all, delete-orphan")
    telegram_accounts: Mapped[List["TelegramAccount"]] = relationship("TelegramAccount", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        Index("idx_user_sessions_user_revoked", "user_id", "is_revoked"),
        Index("idx_user_sessions_expires_at", "expires_at"),
    )

    user: Mapped["User"] = relationship("User", back_populates="sessions")


class AuthVerification(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "auth_verifications"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "type IN ('EMAIL_VERIFICATION', 'PASSWORD_RESET', 'LOGIN_OTP')",
            name="chk_auth_verifications_type"
        ),
        CheckConstraint(
            "attempts_count <= max_attempts",
            name="chk_auth_verifications_attempts"
        ),
        Index("idx_auth_verifications_lookup", "identifier", "type", "expires_at"),
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="verifications")
