```
$ docker run -d -p 5432:5432 -v postgres-data:/var/lib/postgresql -e POSTGRES_PASSWORD=mysecret postgres
17637ad6f87c39fe178e18b0b0fa8909ea7782f57490d6bfba73c7b06596754b
$ docker ps
CONTAINER ID   IMAGE      COMMAND                  CREATED         STATUS
         PORTS                                         NAMES
17637ad6f87c   postgres   "docker-entrypoint.s…"   6 seconds ago   Up 4 seconds
         0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   cool_matsumoto
```
Сейчас в контейнере рекомендуется использовать путь:
```
/var/lib/postgresql
```
При таком подходе образ автоматически создает подкаталог с версиями «PostgreSQL» внутри подключенного тома.
