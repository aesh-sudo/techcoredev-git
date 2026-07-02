Создадим контейнер с «postgres» в сети «my-app-net»:
```bash
$ docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=mysecret --name pg-db --network my-app-net postgres
369eb319dee083e84fc66d0918855eebbbd473f127cf454bbacd8cb5626d5f45
```
```--network``` – параметр для указания сети, к которой должен быть подключен контейнер.
