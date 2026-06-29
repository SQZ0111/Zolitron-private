from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    status = Column(String(30), nullable=False, default="completed")
    model_version = Column(String(80), nullable=False, default="dummy-v1")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    classifications = relationship("Classification", back_populates="analysis_run")
