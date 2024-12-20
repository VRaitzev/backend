from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.mental_plan import MentalPlan, MentalPlanResource
from pydantic import BaseModel
from typing import Optional
router = APIRouter()

# Схема для валидации входящих данных
class MentalPlanCreate(BaseModel):
    user_id: int
    name: str
    goal: str
    resource_list: List[int]
    progress: float = 0.0

class MentalPlanUpdate(BaseModel):
    user_id: Optional[int]
    name: Optional[str]
    goal: Optional[str]
    resource_list: Optional[List[int]]
    progress: Optional[float] = 30.0


@router.post("/mentalPlans/", response_model=dict)
async def create_mental_plan(mental_plan_data: MentalPlanCreate, db: AsyncSession = Depends(get_db)):
    new_mental_plan = MentalPlan(
        user_id=mental_plan_data.user_id,
        name=mental_plan_data.name,
        goal=mental_plan_data.goal
    )

    try:
        # Открываем транзакцию
        async with db.begin():
            db.add(new_mental_plan)
            await db.flush()  # Обновить new_mental_plan.id
            
            # Добавление ресурсов
            resources = [
                MentalPlanResource(
                    mental_plan_id=new_mental_plan.id,
                    resource_id=resource_id,
                    progress=0
                )
                for resource_id in mental_plan_data.resource_list
            ]
            db.add_all(resources)

        await db.commit()
        return {
            "message": "Mental plan created successfully!",
            "mental_plan_id": new_mental_plan.id
        }
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")


@router.patch("/mentalPlans/{id}", response_model=dict)
async def update_mental_plan(id: int, mental_plan_data: MentalPlanUpdate, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Получаем объект физического плана
        query = await db.execute(select(MentalPlan).where(MentalPlan.id == id))
        mental_plan = query.scalars().first()

        if not mental_plan:
            raise HTTPException(status_code=404, detail="Ментальный план не найден!")

        # Обновляем поля через цикл
        update_data = mental_plan_data.dict(exclude_unset=True)
        EXCLUDE_VALUES = [None, '', 0, 0.0]

        for key, value in update_data.items():
            if value not in EXCLUDE_VALUES:
                setattr(mental_plan, key, value)

    # Если нужно быть уверенным в актуальности объекта:
    await db.refresh(mental_plan)

    return {"message": "Ментальный план успешно обновлен!", "resource": mental_plan}