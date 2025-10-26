FROM python:3.12-slim

WORKDIR /app

# Устанавливаем локаль и поддержку кириллицы
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONUTF8=1

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    locales \
    gcc \
    && locale-gen ru_RU.UTF-8 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаём директории
RUN mkdir -p uploads/resumes

# Открываем порт
EXPOSE 8090

# Запускаем приложение
CMD ["python", "-c", "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8090)"]