import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


import os
import time


def generate_uuid7() -> uuid.UUID:
    """Generate time-ordered RFC 9562 UUIDv7."""
    if hasattr(uuid, "uuid7"):
        return uuid.uuid7()
    try:
        import uuid6
        return uuid6.uuid7()
    except ImportError:
        pass

    ns = time.time_ns()
    timestamp_ms = ns // 1_000_000
    time_bytes = timestamp_ms.to_bytes(6, byteorder="big")
    rand_a = int.from_bytes(os.urandom(2), byteorder="big") & 0x0FFF
    ver_and_rand = (0x7000 | rand_a).to_bytes(2, byteorder="big")
    rand_b = int.from_bytes(os.urandom(8), byteorder="big") & 0x3FFFFFFFFFFFFFFF
    var_and_rand = (0x8000000000000000 | rand_b).to_bytes(8, byteorder="big")
    return uuid.UUID(bytes=time_bytes + ver_and_rand + var_and_rand)


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
