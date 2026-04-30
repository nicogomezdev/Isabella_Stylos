from sqlalchemy import Column, Integer, Time, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class BusinessHours(Base):
    __tablename__ = "business_hours"

    id =  Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day_of_week = Column(Integer, nullable=False)
    open_time = Column(Time, nullable=True)
    close_time = Column(Time, nullable=True)
    is_open = Column(Boolean, nullable=True)