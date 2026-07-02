### Задача (Сервис 1: App): Описать наш my-app (из М2) как сервис ###
Напомним код «dockerfile»:
```
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```
Код «docker-compose.yml»:
```
services:
  app:
    build:
      dockerfile: dockerfile
      context: .
    ports:
      - '5000:5000
```
### Задача (Сервис 2: DB): Описать PostgreSQL (из М4) как сервис ###
Напомним запуск «PostgreSQL»:
```bash
$ docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=mysecret postgres
```
Код «docker-compose.yml»:
```
  db:
    image: postgres:14-alpine
    environment:
      - 'POSTGRES_PASSWORD=mysecret'
    ports:
      - '5432:5432
```
Итоговый файл «docker-compose.yml»:
```
services:
  app:
    build:
      dockerfile: dockerfile
      context: .
    ports:
      - '5000:5000'
  db:
    image: postgres:14-alpine
    environment:
      - 'POSTGRES_PASSWORD=mysecret'
    ports:
      - '5432:5432'
```
### Задача (Запуск): Запустить все: docker-compose up ###
```bash
docker compose up
```
### Задача (Фоновый режим): Остановить (Ctrl+C). Запустить в фоне: docker-compose up -d ###
```bash
$ docker compose up -d
[+] up 2/2
 ✔ Container module5-db-1  Started                                                                                             0.7s
 ✔ Container module5-app-1 Started                                                                                             0.6s
```
```-d (detached mode)``` – параметр для запуска контейнера в фоновом режиме.
### Задача (Управление): Посмотреть статус: docker-compose ps. Посмотреть логи: docker-compose logs app, docker-compose logs -f ###
```bash
$ docker compose ps
NAME            IMAGE                COMMAND                  SERVICE   CREATED
       STATUS             PORTS
module5-app-1   module5-app          "python app.py"          app       2 hours ago
       Up About an hour   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
module5-db-1    postgres:14-alpine   "docker-entrypoint.s…"   db        2 hours ago
       Up About an hour   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
```
Чтобы посмотреть логи запущенного контейнера, необходимо выполнить команду:
```bash
docker compose logs [-f] ИМЯ_СЕРВИСА_ИЗ_YML-ФАЙЛА
```
Список запущенных контейнеров в текущем проекте «docker compose»:
```bash
docker compose ps
```
В колонке ```SERVICE``` указаны имена сервисов.

Если запущен один сервис, то имя сервиса можно не указывать.<br>
```-f``` – параметр для просмотра логов в реальном времени.

Примеры:
```bash
$ docker compose logs app
app-1  |  * Serving Flask app 'app'
app-1  |  * Debug mode: off
...

$ docker compose logs db
db-1  | The files belonging to this database system will be owned by user "postgres".
db-1  | This user must also own the server process.
...
```
### Задача (Остановка): Остановить и удалить все: docker-compose down ###
Контейнеры сначала получают сигнал:<br>
```SIGTERM``` – корректное завершение.<br>
Если завершение работы не выполнено за определенное время, то контейнеры получают сигнал:<br>
```SIGKILL``` – принудительное завершение.<br>
Далее остановленные контейнеры удаляются.<br>
Далее удаляется пользовательская сеть, созданная «compose» для проекта – это освобождает IP-адреса.<br>
Пример:
```bash
$ docker compose down
[+] down 3/3
 ✔ Container module5-app-1 Removed                                                                                            10.5s
 ✔ Container module5-db-1  Removed                                                                                             0.5s
 ✔ Network module5_default Removed                                                                                             0.2s
```
### Задача (Сборка): Явно пересобрать образ: docker-compose build. (или docker-compose up --build) ###
```docker compose build``` – команда читает файл «docker-compose.yml», находит секции ```build``` и пересобирает образы по инструкциям в «dockerfile».<br>
```docker-compose build --no-cache``` – для полной пересборки, без использования кеша.<br>
```docker compose up –build``` – команда для сборки и запуска текущего проекта из файла «docker-compose.yml».
