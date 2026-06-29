from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False, unique=True)
    description = Column(String(250), nullable=True)

    labels = relationship("Label", back_populates="category")
    classifications = relationship("Classification", back_populates="category")
