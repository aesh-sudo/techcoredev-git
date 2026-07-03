Добавим в файл «requirements.txt» строку с «redis».

Изменим файл «docker-compose.yml»:
```
services:
  app:
    build:
      dockerfile: dockerfile
      context: .
    environment:
      - 'DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/postgres'
      - 'REDIS_URL=redis://redis:6379/0'
    ports:
      - '5000:5000'
    volumes:
      - .:/app
    command: gunicorn --bind 0.0.0.0:5000 --reload app:app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
  db:
    image: postgres
    environment:
      - 'POSTGRES_PASSWORD=${POSTGRES_PASSWORD}'
    ports:
      - '5432:5432'
    volumes:
      - postgres-data:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
  redis:
    image: redis
    ports:
      - '6379:6379'
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
volumes:
  postgres-data:
    external: true
```
Добавили переменную ```REDIS_URL``` с адресом «redis» в сервис «app».<br>
Добавили зависимость сервиса «app» от корректного запуска сервиса «redis».<br>
Добавили сам сервис «redis».

Изменим файл «app.py»:
```python
from flask import Flask
import psycopg2
import os
import redis
import json

app = Flask(__name__)

redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL'))

@app.route('/')
def hello():
    cached_data = redis_client.get('user_data')
    if cached_data:
        data = json.loads(cached_data)
        source = "Redis (кеш)"
    else:
        database_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        cur.execute('SELECT name, age FROM users ORDER BY id LIMIT 1')
        name, age = cur.fetchone()

        cur.close()
        conn.close()

        data = {"name": name, "age": age}
        redis_client.setex('user_data', 60, json.dumps(data))
        source = "PostgreSQL (БД)"
    return f'''
    <h1>Docker-контейнер</h1>
    <h2>Первая запись в БД:</h2>
    <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
        <p><strong>Имя:</strong> {data['name']}</p>
        <p><strong>Возраст:</strong> {data['age']} лет</p>
        <p><em>Источник данных: {source}</em></p>
    </div>
    '''

@app.route('/clear-cache')
def clear_cache():
    """Эндпоинт для очистки кэша"""
    redis_client.delete('user_data')
    return '<h1>Кэш очищен!</h1><a href="/">Вернуться</a>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
Если данные по запросу есть в кеше, то они берутся оттуда. Если же данных в кеше нет, то выполняется запрос к БД и полученные данные сохраняются в кеш на 60 секунд.

Проверка:<br>
Открыть страницу в браузере – данные будут взяты из БД. Если обновить страницу, то данные будут взяты уже из кеша, о чем сообщит соответствующая запись. Через 60 секунд данные вновь будут взяты из БД.
