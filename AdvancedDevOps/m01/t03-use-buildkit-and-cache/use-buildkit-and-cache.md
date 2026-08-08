Команда сборки образа без использования «BuildKit»:
```bash
DOCKER_BUILDKIT=0 docker build . -t my-app:bk0
```

Команда сборки образа с использованием «BuildKit»:
```bash
DOCKER_BUILDKIT=1 docker build . -t my-app:bk1
```

«BuildKit» по умолчанию используется, поэтому можно не указывать ```DOCKER_BUILDKIT=1``` в команде сборки.

```--mount=type=cache``` – параметр ```RUN``` для создания кеш-монтирования. Механизм позволяет сохранить содержимое определенной директории между запусками сборки.<br>
На стороне билдера (хоста, где выполняется сборка) создается хранилище, которое монтируется в указанную точку образа (```target```) во время выполнения команды ```RUN```, но не попадает в итоговый образ. Это позволяет повторно использовать необходимые для сборки данные.

«dockerfile» с использованием ```--mount=type=cache``` для сборки слоя образа:
```
FROM python:3.11-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN echo "Build timestamp: $(date)"
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

CMD ["python", "--version"]
```
