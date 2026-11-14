
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Text,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class URLCLICK(Base):

    __tablename__ = "url_clicks"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    url_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    referrer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
