from sqlalchemy import Column,Integer,String,ForeignKey, Float, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from pydantic import BaseModel, PositiveInt,PositiveFloat,ValidationError
from ..db import Base

class Image(Base,BaseModel):
    __tablename__ = "Images"
    id: PositiveInt = Column(Integer, primary_key=True,index=True)
    #every image belongs to one city
    city_id: PositiveInt = Column(Integer, ForeignKey("cities.id"), nullable=False)
    source: str = Column(String(50),default="upload")
    file_path: str = Column(String(500), nullable=False)
    latitude: PositiveFloat = Column(Float,nullable=True)
    longitude: PositiveFloat = Column(Float,nullable=True)
    processed_state: str = Column(String(20), default="processed")
    timestamp: datetime = Column(DateTime, default=datetime.now(datetime.timezone.utc))

    city = relationship("City", back_populates="image")
    sites = relationship("Flydump", back_populates="images")

