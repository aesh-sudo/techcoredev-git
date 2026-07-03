Сделаем так, чтобы приложение «app.py» выводило первую строку из БД, которую мы создали и заполнили в «Модуле 4» и которая осталась на хосте в томе ```postgres-data```.

Файл «docker-compose.yml»:
```
services:
  app:
    build:
      dockerfile: dockerfile
      context: .
    environment:
      - 'DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/postgres'     1
    ports:
      - '5000:5000'
  db:
    image: postgres
    environment:
      - 'POSTGRES_PASSWORD=${POSTGRES_PASSWORD}'
    ports:
      - '5432:5432'
    volumes:
      - postgres-data:/var/lib/postgresql

volumes:
  postgres-data:
    external: true                                                                             2
```
```1``` – ```postgres``` – это имя БД, которую мы создали и заполнили в «Модуле 4». Так как там мы не задавали имени БД, то оно автоматически задается аналогичным имени пользователя.<br>
```2``` – ```external: true``` – параметр указывает на то, что ресурс уже создан и надо использовать его.

Файл «app.py»:
```python
from flask import Flask
import psycopg2
import os

app = Flask(__name__)

@app.route('/')
def hello():
    # Подключение к БД
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    # Получение первой записи
    cur.execute('SELECT name, age FROM users ORDER BY id LIMIT 1')
    name, age = cur.fetchone()

    cur.close()
    conn.close()

    return f'''
    <h1>Docker-контейнер</h1>
    <h2>Первая запись в БД:</h2>
    <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
        <p><strong>Имя:</strong> {name}</p>
        <p><strong>Возраст:</strong> {age} лет</p>
    </div>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```
Файл «.env»:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecret
```
Изменили то, что оставили имя пользователя БД то, которое было задано в «Модуле 4».

Файл «requirements.txt»:
```
Flask==3.0.0
psycopg2-binary==2.9.7
```
Добавили ```psycopg2-binary``` - скомпилированная версия библиотеки для работы с «PostgreSQL» в «Python».

В «requirements.txt»:
```
psycopg2-binary==2.9.7
```
а в «app.py»:
```
import psycopg2
```
Это сделано разработчиками библиотеки, чтобы можно было легко переключаться между версиями для разработки (скомпилированная версия) и продакшена. В коде при этом всегда пишется:
```
import psycopg2
```
