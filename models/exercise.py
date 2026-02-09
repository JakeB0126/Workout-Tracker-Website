from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from models.base import Base

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable=False, unique = True, index = True)
    muscle_group = Column(String(50), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    

