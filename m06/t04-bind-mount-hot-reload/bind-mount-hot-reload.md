Изменим файл «dockerfile»:
```
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1                        1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```
```1``` – отключение создания файлов скомпилированного байт-кода (```.pyc```), которые помещаются в каталог ```__pycache__```. Создаются для того, чтобы в следующий раз код загружался быстрее.

В файл «requirements.txt» добавим строку с «Gunicorn» - это WSGI-сервер (```Web Server Gateway Interface```) для общения между веб-сервером и Python-приложением.

Изменим файл «docker-compose.yml»:
```
services:
  app:
    build:
      dockerfile: dockerfile
      context: .
    environment:
      - 'DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/postgres'
    ports:
      - '5000:5000'
    volumes:                                                                                   1
      - .:/app
    command: gunicorn --bind 0.0.0.0:5000 --reload app:app                                     2
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
    external: true
```
```1``` – добавлен том для возможности изменения кода приложения.<br>
```2``` – добавлена команда для запуска веб-сервера «Gunicorn».<br>
```--bind 0.0.0.0:5000``` – обработка запросов, поступающих со всех IP-адресов.<br>
```--reload``` – сервер будет следить за изменениями в файлах и перезапускаться при их сохранении. Используется только для РАЗРАБОТКИ, так как потребляет много ресурсов.

Пример:<br>
Будем брать не первую строку из БД, а последнюю.

Далее можно изменить код в файле приложения «app.py» и при перезагрузке страницы в браузере мы увидим изменения.<br>
Можно даже поменять запрос. Например, брать не первую, а последнюю строку таблицы.
