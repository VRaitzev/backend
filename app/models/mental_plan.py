from sqlalchemy import Column, Integer, String, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class MentalPlan(Base):
    __tablename__ = "mental_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    progress = Column(Integer, default=30)

    user = relationship("User", back_populates="mental_plans")
    resources = relationship("MentalPlanResource", back_populates="mental_plan")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum("book", "course", "video", name="resource_type_enum"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    volume = Column(Float, nullable=False)


class MentalPlanResource(Base):
    __tablename__ = "mental_plan_resources"

    id = Column(Integer, primary_key=True, index=True)
    mental_plan_id = Column(Integer, ForeignKey("mental_plans.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    progress = Column(Float, default=0.0)

    mental_plan = relationship("MentalPlan", back_populates="resources")
    resource = relationship("Resource")

