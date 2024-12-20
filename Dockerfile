# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry (менеджер зависимостей)
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавляем путь к Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# Создаём рабочую директорию в контейнере
WORKDIR /app

# Копируем скрипт wait-for-it.sh
COPY wait-for-it.sh /app/wait-for-it.sh

# Копируем файлы проекта
COPY . /app/

# Устанавливаем зависимости через Poetry
RUN poetry install --no-interaction --no-ansi

# Строка подключения к базе данных
ENV DATABASE_URL=postgresql+asyncpg://application_user:application_user_password@postgres:5432/my_plan_application_db

# Делаем скрипт wait-for-it.sh исполнимым
RUN chmod +x /app/wait-for-it.sh

# Запускаем приложение через Uvicorn
CMD ["/app/wait-for-it.sh", "postgres:5432", "--", "poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
