```bash
$ docker volume create postgres-data
postgres-data

$ docker volume ls
DRIVER    VOLUME NAME
local     postgres-data
```
Созданные таким образом тома располагаются по пути:
```
/var/lib/docker/volumes
```
