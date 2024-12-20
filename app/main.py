from fastapi import FastAPI
from app.routers import user
from app.routers import physical_plan
from app.routers import mental_plan
from app.routers import resourse
from app.routers import outher_tasks
from app.models import User, PhysicalPlan, MentalPlan, Workout, Exercise, WorkoutExercise, OuterTask
from app.core.database import engine  # Подключение к движку из core
from app.core.database import Base
from app.core.database import async_session
from app.default_data import add_default_exercises
from fastapi.middleware.cors import CORSMiddleware
import asyncio

# Создание таблиц
async def create_tables():
    async with engine.begin() as conn:
        # Создание всех таблиц в базе данных
        await conn.run_sync(Base.metadata.create_all)

# Функция для инициализации данных (вставка дефолтных значений)
async def initialize_data():
    async with async_session() as session:
        # Проверяем, есть ли дефолтные упражнения в базе данных
        await add_default_exercises(session)

# Основное приложение FastAPI
app = FastAPI(title="My Plan Application Backend", debug=True)

# Подключаем роуты
app.include_router(user.router)
app.include_router(physical_plan.router)
app.include_router(mental_plan.router)
app.include_router(resourse.router)
app.include_router(outher_tasks.router)

# Обработчик события старта приложения
@app.on_event("startup")
async def on_startup():
    # Создаем таблицы, если их нет
    await create_tables()
    # Добавляем дефолтные данные
    await initialize_data()

@app.get("/")
async def root():
    return {"message": "Welcome to My Plan Application Backend!"}

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (можно настроить конкретные)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все HTTP методы
    allow_headers=["*"],  # Разрешить все заголовки
)
