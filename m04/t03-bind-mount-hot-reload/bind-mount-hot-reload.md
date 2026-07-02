Файл приложения на Python – «app.py»:
```python
async def app(scope, receive, send):
    if scope['type'] == 'http':
        await send({                                          1
            'type': 'http.response.start',
            'status': 200,
            'headers': [(b'content-type', b'text/plain')],
        })
        await send({                                          2
            'type': 'http.response.body',
            'body': b'Hello with reload!!!',
        })
```
```app``` – имя точки входа в приложение (по умолчанию).<br>
```scope``` – паспорт запроса. ```URL```, метод (```GET``` или ```POST```), заголовки и тип соединения.<br>
```send``` – функция для отправки данных обратно клиенту (браузеру).<br>
```1``` – отправка заголовка HTTP-ответа.<br>
```2``` – отправка тела HTTP-ответа.

dockerfile:
```
FROM python:3.11-slim AS builder
RUN pip install --no-cache-dir --target=/install uvicorn                                       1

FROM python:3.11-slim
COPY --from=builder /install /install
ENV PYTHONPATH=/install                                                                        2
ENV PYTHONDONTWRITEBYTECODE=1                                                                  3

WORKDIR /app
COPY app.py .
CMD ["/install/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]     4
```
```1``` – установка пакета ASGI-сервера (Asynchronous Server Gateway Interface) – интерфейс для взаимодействия между веб-сервером и Python-приложением.<br>
```--target``` – указание места (не по умолчанию) для установки пакета.

```2``` – установка переменной окружения для обнаружения файлов установленного пакета «uvicorn».<br>
```3``` – отключение создания файлов скомпилированного байт-кода (```.pyc```), которые помещаются в каталог ```__pycache__```. Создаются для того, чтобы в следующий раз код загружался быстрее.

```4``` – команда, выполняемая при запуске контейнера.<br>
```/install/bin/uvicorn``` – запуск исполняемого файла.<br>
```app:app``` – сигнал «uvicorn» для запуска приложения, находящегося в файле «app.py» в переменной ```app```. Конструкция:
```
файл:переменная
```
```--reload``` – сервер будет следить за изменениями в файлах и перезапускаться при их сохранении. Используется только для РАЗРАБОТКИ, так как потребляет много ресурсов.

Соберем образ:
```bash
docker build -t bind_mount_py_app .
```
Запустим контейнер:
```bash
$ docker run --rm -p 5000:5000 -v $(pwd):/app bind_mount_py_app
```
Изменим в файле «app.py» выводимый текст. В логах запущенного контейнера при этом появятся записи:
```
WARNING:  StatReload detected changes in 'app.py'. Reloading...
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [8]
INFO:     Started server process [9]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```
При перезагрузке страницы в браузере мы увидим изменения.
