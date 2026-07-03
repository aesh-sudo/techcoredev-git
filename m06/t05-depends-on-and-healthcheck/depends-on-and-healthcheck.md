### Задача (depends_on): Гарантировать порядок запуска ###
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
    volumes:
      - .:/app
    command: gunicorn --bind 0.0.0.0:5000 --reload app:app
    depends_on:
      - 'db'
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
При запуске приложения в логах можно увидеть, что сервис «bd» запускается раньше, чем сервис «app».
### Задача (healthcheck): Добавить healthcheck в db ###
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
    volumes:
      - .:/app
    command: gunicorn --bind 0.0.0.0:5000 --reload app:app
    depends_on:
      - 'db'
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
volumes:
  postgres-data:
    external: true
```
```test``` – ключ для задания команды проверки здоровья контейнера.<br>
```CMD-SHELL``` – формат передачи команды в «Docker». Команда будет выполнена через стандартную командную оболочку контейнера (эквивалент ```/bin/sh -c "команда"```). Это позволяет использовать возможности «shell».<br>
```pg_isready``` – утилита «PostgresSQL» для проверки статуса соединения с сервером БД. Если БД готова к работе, то утилита вернет код ```0``` (ноль) - успех.<br>
```-U``` – параметр для указания имени пользователя БД, от имени которого будет выполнена проверка подключения к БД.

Запустим приложение и проверим cписок запущенных контейнеров в текущем проекте «Docker Compose»:
```bash
$ docker compose ps
NAME              IMAGE           COMMAND                  SERVICE   CREATED
          STATUS                    PORTS
module6_2-app-1   module6_2-app   "gunicorn --bind 0.0…"   app       16 seconds ago
          Up 15 seconds             0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
module6_2-db-1    postgres        "docker-entrypoint.s…"   db        40 seconds ago
          Up 16 seconds (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
```
### Задача (depends_on + healthcheck): Сделать, чтобы app ждал здорового db ###
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
    volumes:
      - .:/app
    command: gunicorn --bind 0.0.0.0:5000 --reload app:app
    depends_on:
      db:
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
volumes:
  postgres-data:
    external: true
```
```condition``` – статус состояния зависимого сервиса в директиве ```depends_on```. Может иметь три значения:<br>
```service_started``` – значение по умолчанию. То есть, можно не указывать и просто записать как:
```
depends_on:
  - ‘db’
```
Проблема может возникнуть из-за того, что контейнер запустится, а сам сервис будет еще не готов к работе.

```service_healthy``` – сервис будет запущен только после того, как ```healthcheck``` сервиса, который должен запуститься раньше, вернет статус ```healthy```.
В зависимом сервисе обязательно должен быть определен ```healthcheck```.

```service_completed_successfully``` – зависимый сервис ждет, пока сервис, от которого он зависит, завершит свою работу успешно.
