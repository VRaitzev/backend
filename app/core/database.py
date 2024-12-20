# app/core/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Строка подключения к базе данных с использованием асинхронного драйвера
DATABASE_URL = "postgresql+asyncpg://application_user:application_user_password@postgres:5432/my_plan_application_db"

# Создаем базу
Base = declarative_base()

# Настроим асинхронный движок
engine = create_async_engine(DATABASE_URL, future=True, echo=False)

# Настроим сессию
async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Асинхронный генератор для получения сессии
async def get_db():
    async with async_session() as session:
        yield session
