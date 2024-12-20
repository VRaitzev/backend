from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    physical_plan_id = Column(Integer, ForeignKey("physical_plans.id"))
    day_of_week = Column(Integer, nullable=False)

    physical_plan = relationship("PhysicalPlan", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    calories_burned = Column(Float, nullable=False)
    description = Column(Text)
    start_reps = Column(Integer, nullable=False)
    end_reps = Column(Integer, nullable=False)
    step = Column(Integer, nullable=False)


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))

    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise")
