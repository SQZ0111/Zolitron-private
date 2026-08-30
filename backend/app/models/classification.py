from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Classification(Base):
    __tablename__ = "classifications"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    label_id = Column(Integer, ForeignKey("labels.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(String(30), nullable=False, default="classified")
    bbox_x = Column(Float, nullable=True)
    bbox_y = Column(Float, nullable=True)
    bbox_width = Column(Float, nullable=True)
    bbox_height = Column(Float, nullable=True)
    disposition = Column(String(20), nullable=True)
    garbage_coverage = Column(Float, nullable=True)
    litter_coverage = Column(Float, nullable=True)
    garbage_count = Column(Integer, nullable=True)
    litter_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    image = relationship("Image", back_populates="classifications")
    label = relationship("Label", back_populates="classifications")
    category = relationship("Category", back_populates="classifications")
    analysis_run = relationship("AnalysisRun", back_populates="classifications")
    detections = relationship(
        "Detection",
        back_populates="classification",
        cascade="all, delete-orphan",
    )
