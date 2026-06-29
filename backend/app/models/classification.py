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
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    image = relationship("Image", back_populates="classifications")
    label = relationship("Label", back_populates="classifications")
    category = relationship("Category", back_populates="classifications")
    analysis_run = relationship("AnalysisRun", back_populates="classifications")
