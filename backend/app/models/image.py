from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, default="dummy")
    img_url = Column(String(500), nullable=False)
    storage_path = Column(String(500), nullable=True)
    city = Column(String(120), nullable=False)
    country = Column(String(120), nullable=False, default="Germany")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(30), nullable=False, default="classified")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    classifications = relationship("Classification", back_populates="image")
