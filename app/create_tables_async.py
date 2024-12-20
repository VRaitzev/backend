# create_tables_async.py

import asyncio
from .core.database import engine, Base  # Используем уже настроенный engine и Base из вашего файла
from .models.user import User
from .models.physical_plan import PhysicalPlan
from .models.mental_plan import MentalPlan, Resource, MentalPlanResource
from .models.workout import Workout, Exercise, WorkoutExercise
from .models.outher_task import OuterTask
# Асинхронная функция для создания таблиц
async def create_tables():
    # Создаём все таблицы, определённые в Base (включая модели User, PhysicalPlan и другие)
    async with engine.begin() as conn:
        # Мы используем conn.run_sync, чтобы синхронно запустить создание всех таблиц
        await conn.run_sync(Base.metadata.drop_all)
        # await conn.run_sync(Base.metadata.create_all)

    print("Таблицы созданы!")

# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(create_tables())
