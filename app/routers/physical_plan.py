from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models import PhysicalPlan, Workout, WorkoutExercise, Exercise
from pydantic import BaseModel
from sqlalchemy.future import select
from typing import Optional
router = APIRouter()

# Схема для валидации входящих данных
class PhysicalPlanCreate(BaseModel):
    user_id: int
    goal: str
    age: int
    gender: str
    weight: float
    height: float
    bmi: float

class PhysicalPlanUpdate(BaseModel):
    user_id: Optional[int] = 0
    goal: Optional[str] = ''
    age: Optional[int] = 0
    gender: Optional[str] = ''
    weight: Optional[float] = 0.0
    height: Optional[float] = 0.0
    bmi: Optional[float] = 0.0
    day: Optional[int] = 0
    progress: Optional[float] = 0.0



@router.post("/physicalPlans/", response_model=dict)
async def create_physical_plan(
    physical_plan_data: PhysicalPlanCreate,
    db: AsyncSession = Depends(get_db)
):
    # Создаём физический план
    new_physical_plan = PhysicalPlan(
        user_id=physical_plan_data.user_id,
        goal=physical_plan_data.goal,
        age=physical_plan_data.age,
        gender=physical_plan_data.gender,
        weight=physical_plan_data.weight,
        height=physical_plan_data.height,
        bmi=physical_plan_data.bmi,
        progress=0,
    )

    try:
        # Добавляем новый физический план и подтверждаем изменения
        db.add(new_physical_plan)
        await db.commit()
        await db.refresh(new_physical_plan)

        # Создаём тренировки для каждого дня недели
        workouts = [
            Workout(
                physical_plan_id=new_physical_plan.id,
                day_of_week=i,
            )
            for i in range(1, 8)
        ]
        db.add_all(workouts)
        await db.commit()

        # Извлекаем первые 8 упражнений из базы данных
        result = await db.execute(select(Exercise).order_by(Exercise.id).limit(8))
        exercises = result.scalars().all()

        # Связываем тренировки с упражнениями
        for workout in workouts:
            for exercise in exercises:
                workout_exercise = WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=exercise.id,
                )
                db.add(workout_exercise)

        # Сохраняем все изменения
        await db.commit()

        return {"message": "Physical plan and workouts created successfully!"}

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400, detail=f"An error occurred: {str(e)}"
        )


@router.patch("/physicalPlans/{id}", response_model=dict)
async def update_physical_plan(id: int, physical_plan_data: PhysicalPlanUpdate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Получаем объект физического плана
        query = await db.execute(select(PhysicalPlan).where(PhysicalPlan.id == id))
        physical_plan = query.scalars().first()

        if not physical_plan:
            raise HTTPException(status_code=404, detail="Ресурс не найден!")

        # Обновляем поля через цикл
        update_data = physical_plan_data.dict(exclude_unset=True)
        EXCLUDE_VALUES = [None, '', 0, 0.0]

        for key, value in update_data.items():
            if value not in EXCLUDE_VALUES:
                setattr(physical_plan, key, value)

    # Если нужно быть уверенным в актуальности объекта:
    await db.refresh(physical_plan)

    return {"message": "Ресурс успешно обновлен!", "resource": physical_plan}
