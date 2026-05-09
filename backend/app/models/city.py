from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,ForeignKey, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel, PositiveInt,PositiveFloat,ValidationError
from ..db import Base

class City(Base,BaseModel):
    __tablename__ = 'cities'

    id: PositiveInt = Column(Integer, primary_key=True,index=True)
    name: str = Column(String(250), nullable=False,unique=True)
    postal: PositiveInt = Column(Integer,nullable=False)
    latitude: PositiveFloat = Column(Float,nullable=False)
    longitude: PositiveFloat= Column(Float,nullable=False)



    #need to look on those
    images = relationship("Image", back_populates="city")
    sites = relationship("Flydump", back_populates="city")

    def __repr__(self):
        return f"<City> - {self.name}\nLatititude,Longitude>-({self.latitude},{self.longitude})"

