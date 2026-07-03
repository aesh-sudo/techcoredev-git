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
