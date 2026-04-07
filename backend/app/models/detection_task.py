from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.base import Base


class DetectionTask(Base):
    __tablename__ = "detection_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_no = Column(String(64), unique=True, nullable=False, index=True)
    location_name = Column(String(255), nullable=True)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    remark = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="processing")
    total_score = Column(Float, nullable=True)
    level = Column(String(32), nullable=True)
    blue_risk = Column(Boolean, nullable=False, default=False)
    satellite_score = Column(Float, nullable=True)
    ecology_score = Column(Float, nullable=True)
    image_score = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    images = relationship(
        "DetectionImage",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="DetectionImage.id",
    )
    result = relationship(
        "DetectionResult",
        back_populates="task",
        uselist=False,
        cascade="all, delete-orphan",
    )
    warning = relationship(
        "WarningRecord",
        back_populates="task",
        uselist=False,
        cascade="all, delete-orphan",
    )
