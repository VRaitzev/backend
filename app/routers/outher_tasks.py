from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.core.database import get_db
from app.models.outher_task import OuterTask  # Импорт модели задачи
from pydantic import BaseModel, Field
from app.auth.authenticate import authenticate

router = APIRouter()

# Pydantic модели для задач
class OuterTaskUpdate(BaseModel):
    title: str | None = Field(None, example="Обновленное название задачи")
    status: bool | None = Field(None, example=True)

class OuterTaskCreate(BaseModel):
    user_id: int = Field(..., example=1)  # ID пользователя
    title: str = Field(..., example="Новая задача")  # Название задачи
    status: bool = Field(False, example=False)  # Статус задачи (по умолчанию False)

class OuterTaskResponse(BaseModel):
    id: int
    title: str
    status: bool
    user_id: int

    class Config:
        orm_mode = True  # Указывает, что можно работать с объектами SQLAlchemy

# Получить все задачи
@router.get("/outherTasks/", response_model=list[OuterTaskResponse])
async def get_all_tasks(db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(OuterTask).options(joinedload(OuterTask.user)))  # Подгружаем пользователя
    tasks = query.scalars().all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Задачи не найдены")
    return tasks

# Создать новую задачу
@router.post("/outherTasks/", response_model=OuterTaskResponse, status_code=201)
async def create_task(task_data: OuterTaskCreate, db: AsyncSession = Depends(get_db)):
    # Создание новой задачи
    new_task = OuterTask(
        user_id=task_data.user_id,
        title=task_data.title,
        status=task_data.status,
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

# Обновить задачу по ID
@router.patch("/outherTasks/{task_id}", response_model=OuterTaskResponse)
async def update_task(task_id: int, task_data: OuterTaskUpdate, db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(OuterTask).where(OuterTask.id == task_id))
    task = query.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Обновление данных задачи
    update_data = task_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    await db.commit()
    await db.refresh(task)
    return task

# Удалить задачу по ID
@router.delete("/outherTasks/{task_id}", response_model=dict)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    query = await db.execute(select(OuterTask).where(OuterTask.id == task_id))
    task = query.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    await db.delete(task)
    await db.commit()
    return {"message": f"Задача с ID {task_id} успешно удалена"}
