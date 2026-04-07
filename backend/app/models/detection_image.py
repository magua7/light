from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class DetectionImage(Base):
    __tablename__ = "detection_images"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("detection_tasks.id"), nullable=False, index=True)
    direction = Column(String(16), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    task = relationship("DetectionTask", back_populates="images")
