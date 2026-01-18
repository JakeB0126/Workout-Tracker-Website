from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable=False)
    muscle_group = Column(String(50), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    

