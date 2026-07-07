За основу возьмем приложение из М2.<br>
Создадим каталоги и разместим необходимые файлы по ним:<br>
Каталог ```src``` - файлы приложения на «Python».<br>
```app.py``` – файл приложения:
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Hello, World!!! Я работаю внутри Docker-контейнера!!!</h1>'

if __name__ == '__main__':
    # host='0.0.0.0' открывает доступ к приложению извне контейнера
    app.run(host='0.0.0.0', port=5000)
```

```requirements.txt``` - файл необходимых для работы приложения зависимостей:
```
Flask==3.0.0
```

Каталог ```tests``` - файлы с тестами для приложения и необходимыми для выполнения кода тестирования зависимостями.<br>
```__init__.py``` – файл для того, чтобы «Python» воспринимал каталог как «пакет» (```package```), в котором находятся модули.<br>
```test_app.py``` – файл с процедурой тестирования:
```python
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200


def test_hello_world_content(client):
    response = client.get('/')
    data = response.data.decode('utf-8')
    assert 'Hello, World!!!' in data
    assert 'Docker-контейнера' in data


def test_hello_world_html(client):
    response = client.get('/')
    data = response.data.decode('utf-8')
    assert '<h1>' in data
    assert '</h1>' in data


def test_hello_world_is_string(client):
    response = client.get('/')
    assert response.content_type == 'text/html; charset=utf-8'


def test_nonexistent_route(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404
```

```requirements.txt``` - файл необходимых для работы тестов зависимостей:
```
pytest
Flask==3.0.0
```

Каталог ```docker``` - для хранения «dockerfile»:
```
FROM python:3.10-slim
WORKDIR /app
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

Код файла воркфлоу ```ci.yml```:
```
name: ci
on:
  pull_request:
    branches:
      - main
    path:
      - 'm08/t04-docker-build-and-push/**'
      - '!m08/t04-docker-build-and-push/*.md'
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: m08/t04-docker-build-and-push
    steps:
      - name: checkout
        uses: actions/checkout@v7

      - name: login to GHCR
        uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: setup
        uses: actions/setup-python@v6
        with:
          python-version: '3.10'

      - name: run
        run: |
          pip install -r tests/requirements.txt
          PYTHONPATH=src pytest tests/                                         1

      - name: build and push
        uses: docker/build-push-action@v7
        with:
          context: ./m08/t04-docker-build-and-push                             2
          file: ./m08/t04-docker-build-and-push/docker/dockerfile              3
          push: true
          tags: ghcr.io/aesh-sudo/m08-t04-docker-build-and-push:latest
```

```1``` – в файле тестов есть код ```from app import app```. По умолчанию «Python» будет искать файл «app.py» в корне проекта. Указание в переменной окружения значения ```src``` задает дополнительный путь, где «Python» выполнит поиск файлов с тестами.

```2``` – каталог, который «Docker» будет считать корневым.

```3``` – путь к «dockerfile». Указывается относительно корня репозитория, так как «action» выполняет поиск файла на диске раннера. «GH Actions» находит «dockerfile» и передает в «Docker», указывая ```context``` как место, откуда брать файлы для ```COPY```.
