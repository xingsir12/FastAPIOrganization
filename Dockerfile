FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование только необходимых файлов для установки зависимостей
COPY pyproject.toml alembic.ini ./
COPY alembic/ ./alembic/
COPY app/ ./app/

# Установка Python зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Создание скрипта запуска
RUN echo '#!/bin/sh\n\
alembic upgrade head\n\
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh \
    && chmod +x /app/start.sh

# Запуск приложения
CMD ["/app/start.sh"]