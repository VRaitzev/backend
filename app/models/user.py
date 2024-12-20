from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    physical_plans = relationship("PhysicalPlan", back_populates="user")
    mental_plans = relationship("MentalPlan", back_populates="user")
    tasks = relationship("OuterTask", back_populates="user")
