from fastapi import Depends
from app.models import Exercise
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для добавления стандартных упражнений в таблицу
async def add_default_exercises(session: AsyncSession):
    # Проверяем, есть ли хотя бы одна запись в таблице `Exercise`
    result = await session.execute(select(Exercise).limit(1))
    exercise_exists = result.scalars().first() is not None
    logger.info("Запуск функции добавления дефолтных упражнений")
    if not exercise_exists:
        # Если таблица пуста, вставляем данные
        exercises_data = [
            ('Отжимания', 7.5, 'Укрепление мышц груди, рук и плечей. Выполняются на полу с ровной спиной.', 5, 25, 2),
            ('Приседания', 5.0, 'Укрепление ног и ягодиц. Можно выполнять с весом или выпрыгиванием.', 10, 50, 4),
            ('Скручивания на пресс', 3.5, 'Укрепление прямых мышц живота. Выполняются лёжа на спине.', 15, 45, 3),
            ('Выпады', 5.5, 'Проработка ягодиц и бедер. Выполняются с шагами вперёд или назад.', 8, 40, 4),
            ('Бёрпи', 9.0, 'Комплексное упражнение для всего тела и кардиосистемы.', 5, 20, 1),
            ('Подъёмы на носки стоя', 2.0, 'Укрепление икроножных мышц. Выполняются с собственным весом.', 15, 45, 5),
            ('Горные альпинисты', 6.5, 'Интенсивное упражнение для пресса и кардионагрузки. Выполняется в упоре.', 20, 60, 5),
            ('Ягодичный мостик', 4.0, 'Укрепление ягодиц и нижней части спины. Можно усложнить поднятием ноги.', 10, 40, 3),
        ]
        
        # Добавляем данные в таблицу
        for exercise in exercises_data:
            new_exercise = Exercise(
                name=exercise[0],
                calories_burned=exercise[1],
                description=exercise[2],
                start_reps=exercise[3],
                end_reps=exercise[4],
                step=exercise[5]
            )
            session.add(new_exercise)
        
        # Сохраняем изменения
        await session.commit()