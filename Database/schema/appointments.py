from sqlalchemy import Column, String, Date, Time, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from .base import Base
import uuid
from datetime import datetime, timezone



class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("idx_name_date_time", "name", "date"),
        {"schema": "appointment"}
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(String, nullable=False, index=True)

    date = Column(Date, nullable=False)

    reason=Column(String,default="")

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )