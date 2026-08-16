Создадим python-приложение – файл «app.py»:
```python
import os
import time

# Читаем переменную окружения, чтобы понять, где мы работаем
env = os.getenv("ENV", "production")
print(f"App is running in [{env}] environment!")

# Бесконечный цикл, чтобы контейнер не падал
while True:
    time.sleep(5)
```

Создадим «dockerfile»:
```
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]
```

Создадим базовый файл «docker-compose.yml» - для «production»:
```
services:
  web:
    # Скачиваем готовый образ
    image: my-app:latest
    ports:
      - "8080:8080"
    environment:
      - ENV=production
      - PYTHONUNBUFFERED=1
```

Создадим файл переопределения (```docker-compose.override.yml```) - для «development». Этот файл «Docker Compose» читает, если он присутствует в том же каталоге, что и основной файл конфигурации:
```
services:
  web:
    # Собираем образ из «dockerfile»
    build: .

    # Монтируем volume для удобства разработки
    volumes:
      - .:/app

    # Переопределяем переменную окружения
    environment:
      - ENV=development
```

Механизм действия:<br>
Команда «docker compose up» читает файл:
```
docker-compose.yml
```
и выполняет поиск файла:
```
docker-compose.override.yml
```
Если override-файл найден, то выполняется слияние и переопределения из override-файла заменяют или дополняют базовые настройки.

Итоговая конфигурация для «development» выглядит примерно так:
```
services:
  web:
    image: my-app:latest  # Из базы
    build: .              # Из override (при локальном запуске приоритет выше)
    ports: ["8080:8080"]  # Из базы
    volumes: [".:/app"]   # Из override
    environment: 
      - ENV=development   # Из override (при локальном запуске перезапишет значение «production»)
```

Команда для просмотра итоговой конфигурации:
```bash
docker compose config
```

Запустим приложение стандартной командой:
```bash
$ docker compose up –build
web-1  | App is running in [development] environment!
```

Проверим, активен ли «volume»:
```bash
$ docker compose exec web ls -la /app
...
-rw-rw-r-- 1 1000 1000  331 Aug 15 15:06 app.py
-rw-rw-r-- 1 1000 1000  502 Aug 14 10:31 docker-compose.override.yml
-rw-rw-r-- 1 1000 1000  323 Aug 15 15:03 docker-compose.yml
-rw-rw-r-- 1 1000 1000   74 Aug 15 15:05 dockerfile
```

Вывод:<br>
переопределение выполнено, так как «volume» активен.

Чтобы запустить «production», необходимо явно указать файл «Docker Compose»:
```bash
$ docker compose -f docker-compose.yml up
...
web-1  | App is running in [production] environment!
```

Проверим наличие «volume»:
```bash
$ docker compose -f docker-compose.yml exec web ls -la /app
...
-rw-rw-r-- 1 root root  331 Aug 15 15:06 app.py
```

Вывод:
увидели только файл приложения «app.py», который находится в контейнере.
