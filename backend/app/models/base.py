import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


def generate_uuid7() -> uuid.UUID:
    """Generate time-ordered UUIDv7."""
    return uuid.uuid7()


class UUIDPrimaryKeyMixin:
    """Mixin for time-ordered UUIDv7 primary key."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=generate_uuid7,
    )


class TimestampMixin:
    """Mixin for created_at and updated_at with timezone."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft-delete timestamp."""
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
