from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.mental_plan import MentalPlan, MentalPlanResource, Resource
from pydantic import BaseModel
from typing import List
from typing import Optional
from sqlalchemy.orm import selectinload

from app.auth.authenticate import authenticate

router = APIRouter()

# Схема для валидации входящих данных
class ResourceCreate(BaseModel):
    user_id: int
    type: str
    name: str
    description: str
    volume: int

class FreeResourceCreate(BaseModel):
    type: str
    name: str
    description: str
    volume: int
    progress : Optional[int] 

@router.post("/resources/bulk/", response_model=List[int])
async def create_resources(resources_data: List[FreeResourceCreate], db: AsyncSession = Depends(get_db)):
    created_ids = []
    try:
        for resource_data in resources_data:
            new_resource = Resource(
                description = resource_data.description,
                type=resource_data.type,
                name=resource_data.name,
                volume=resource_data.volume
            )
            db.add(new_resource)
            await db.flush()  # Генерирует ID ресурса перед коммитом
            created_ids.append(new_resource.id)
        
        await db.commit()
        return created_ids
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
        status_code=400,
        detail=f"Integrity error occurred while adding resources: {str(e)}"
        )

@router.post("/resources/", response_model=dict)
async def create_resource(resource_data: ResourceCreate, db: AsyncSession = Depends(get_db)):
    print("SIGN")
    new_resource = Resource(
        type=resource_data.type,
        name=resource_data.name,
        description=resource_data.description,
        volume = resource_data.volume
    )
    async with db.begin():
        
        db.add(new_resource)
        await db.flush()
        query = await db.execute((select(MentalPlan).where(MentalPlan.user_id == resource_data.user_id)))
        mental_plan = query.scalars().first()
        if not mental_plan:
            raise HTTPException(status_code=404, detail="Mental plan for this user not found.")
        mental_plan_resource = MentalPlanResource(
                    mental_plan_id=mental_plan.id,
                    resource_id=new_resource.id,
                    progress=0
                )
        db.add(mental_plan_resource)
        await db.commit()
        return {"data": new_resource.id}

@router.delete("/resources/{id}", response_model=dict)
async def delete_resource(
    id: int, 
    user: str = Depends(authenticate),  # Аутентификация пользователя
    db: AsyncSession = Depends(get_db)  # Сессия базы данных
):
    async with db.begin():  # Используем асинхронный контекстный менеджер для транзакции
        # 1. Получаем ресурс по ID
        result = await db.execute(select(Resource).filter(Resource.id == id))
        resource = result.scalars().first()

        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        # 2. Удаляем все связанные записи в таблице MentalPlanResource
        await db.execute(
            "DELETE FROM mental_plan_resources WHERE resource_id = :id",
            {"id": id}
        )

        # 3. Удаляем сам ресурс
        await db.delete(resource)

        # 4. Подтверждаем изменения в базе данных
        await db.commit()  # Асинхронное подтверждение изменений

    # Возвращаем сообщение об успешном удалении
    return {"detail": "Ресурс успешно удален", "id": id}


@router.patch("/resources/{id}", response_model=dict)
async def update_resource(
    id: int, 
    resource_data: FreeResourceCreate, 
    user: str = Depends(authenticate),
    db: AsyncSession = Depends(get_db)
):
    async with db.begin():  # Используем db.begin(), чтобы начать транзакцию
        # Получаем основной ресурс
        query = await db.execute(
            select(Resource).where(Resource.id == id)
        )
        resource = query.scalars().first()

        if not resource:
            raise HTTPException(status_code=404, detail="Ресурс не найден!")

        # Если progress передан, обновляем связанную запись в MentalPlanResource
        if resource_data.progress is not None:
            mpr_query = await db.execute(
                select(MentalPlanResource)
                .where(MentalPlanResource.resource_id == id)
            )
            mental_plan_resource = mpr_query.scalars().first()

            if not mental_plan_resource:
                raise HTTPException(status_code=404, detail="Связь с MentalPlanResource не найдена!")

            # Обновляем progress для найденного ресурса
            mental_plan_resource.progress = resource_data.progress

        # Обновляем поля ресурса
        resource.type = resource_data.type
        resource.name = resource_data.name
        resource.description = resource_data.description
        resource.volume = resource_data.volume

        # Нет необходимости в db.refresh, так как изменения автоматически сохраняются при commit
        await db.commit()  # Явный commit для сохранения изменений в базе данных

    return {"message": "Ресурс успешно обновлен!", "resource": resource}



        
    


