# Пример Dockerfile для Django

# Базовый образ
FROM python:3.10-slim

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y build-essential git libpq-dev && rm -rf /var/lib/apt/lists/*

# Создаём директорию для проекта
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

# Копируем код проекта
COPY . /app/ 

# Запускаем сборку статических файлов (если нужно)
# RUN python manage.py collectstatic --noinput

ENV PYTHONUNBUFFERED=1

CMD ["bash", "run.sh"]