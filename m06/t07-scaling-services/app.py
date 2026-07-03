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
