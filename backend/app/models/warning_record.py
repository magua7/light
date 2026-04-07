from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class WarningRecord(Base):
    __tablename__ = "warning_records"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("detection_tasks.id"), nullable=False, unique=True)
    warning_level = Column(String(32), nullable=False)
    process_status = Column(String(32), nullable=False, default="未处理")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    task = relationship("DetectionTask", back_populates="warning")
