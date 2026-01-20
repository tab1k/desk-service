# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY backend/requirements.txt /app/

# Устанавливаем Python зависимости
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем проект
COPY backend/ /app/

# Создаем директорию для статических файлов
RUN mkdir -p /app/staticfiles

# Собираем статические файлы
RUN python manage.py collectstatic --noinput || true

# Открываем порт
EXPOSE 8000

# Запускаем сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
