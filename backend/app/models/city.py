# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Zolitron
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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

