from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("detection_tasks.id"), nullable=False, unique=True)
    ai_summary_json = Column(Text, nullable=False)
    suggestions_json = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    task = relationship("DetectionTask", back_populates="result")
