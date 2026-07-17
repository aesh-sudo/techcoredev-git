from flask import Flask, Response
import psycopg2
import os
from prometheus_client import Counter, generate_latest

app = Flask(__name__)

# Счетчик вызовов главной страницы
REQUEST_COUNT = Counter('app_hello_requests_total', 'Total number of requests to the main page')

@app.route('/')
def hello():
    # Увеличиваем счетчик на 1 при каждом заходе на страницу
    REQUEST_COUNT.inc()

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

# Маршрут для метрик "Prometheus"
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain; charset=utf-8')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
