Создадим «app.py» – файл приложения:
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello, World! Я работаю внутри Docker-контейнера!</h1>'

if __name__ == '__main__':
    # host='0.0.0.0' открывает доступ к приложению извне контейнера
    app.run(host='0.0.0.0', port=5000)
```
Создадим «requirements.txt» – файл, в котором указываются зависимости, необходимые приложению:
```bash
Flask==3.0.0
```
