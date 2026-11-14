
import uuid 
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Boolean,
    BigInteger,
    DateTime,
    ForeignKey,
    Uuid,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class URL(Base):
    __tablename__ = "urls"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    original_url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    short_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    click_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )    
