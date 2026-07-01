dockerfile_health:
```
FROM nginx:alpine
RUN apk add --no-cache curl											                                                                                     2
RUN echo "OK" > /usr/share/nginx/html/health.html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD curl --fail http://localhost:80/health.html || exit 1		 4
```
```2``` – установка ```curl``` с помощью ```apk``` - пакетного менеджера «Alpine».<br>
```add``` – команда для установки нового пакета.<br>
```--no-cache``` – отключение кеширования индексов пакетов. Индекс не сохраняется, а загружается и сразу используется в ОП.

```4``` – проверка.<br>
```--interval``` – интервал, с каким будет запускаться проверка. В примере – через каждые 30 секунд.<br>
```--timeout``` – максимальное время выполнения команды. В примере – команда ```curl``` должна выполниться менее, чем за 3 секунды.<br>
```--start-period``` – время после старта контейнера, через которое будет выполнена первая проверка. В примере – через 10 секунд.<br>
```--retries``` – количество неудачных попыток, после которого статус работы контейнера поменяется.<br>
```--fail``` – если код ответа >= 400, то ```curl``` завершает работу с кодом 22.

Проверки будут выполняться пока работает контейнер.

Соберем образ и запустим контейнер:
```bash
docker build -f dockerfile_health -t health .
docker run -d --name health -p 8081:80 --rm health

Проверка статуса:
$ docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS
                            PORTS                                     NAMES
a9192b72dbf4   health    "/docker-entrypoint.…"   4 seconds ago   Up 4 seconds (health: starting)
                            0.0.0.0:8081->80/tcp, [::]:8081->80/tcp   health
$ docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS
                   PORTS                                     NAMES
a9192b72dbf4   health    "/docker-entrypoint.…"   8 seconds ago   Up 8 seconds (healthy)
                   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp   health
```
