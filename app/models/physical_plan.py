from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class PhysicalPlan(Base):
    __tablename__ = "physical_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum("male", "female", name="gender_enum"), nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    bmi = Column(Float)
    progress = Column(Float, default=0.0)
    day = Column(Integer, default=1)

    user = relationship("User", back_populates="physical_plans")
    workouts = relationship("Workout", back_populates="physical_plan")
