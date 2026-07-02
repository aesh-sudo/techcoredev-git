Создадим контейнер с «ubuntu», который будет находиться в той же сети, что и контейнер «pg-db». Сразу при запуске войдем в него и установим пакет с программой «ping»:
```bash
$ docker run --rm -it --name pg_ub --network my-app-net ubuntu /bin/bash
# apt-get update && apt-get install -y iputils-ping
```

Пропингуем контейнер «pg-db» по DNS-имени и по IP-адресу:
```bash
# ping pg-db
PING pg-db (172.18.0.2) 56(84) bytes of data.
64 bytes from pg-db.my-app-net (172.18.0.2): icmp_seq=1 ttl=64 time=0.217 ms
64 bytes from pg-db.my-app-net (172.18.0.2): icmp_seq=2 ttl=64 time=0.094 ms
64 bytes from pg-db.my-app-net (172.18.0.2): icmp_seq=3 ttl=64 time=0.095 ms

# ping 172.18.0.2
PING 172.18.0.2 (172.18.0.2) 56(84) bytes of data.
64 bytes from 172.18.0.2: icmp_seq=1 ttl=64 time=0.243 ms
64 bytes from 172.18.0.2: icmp_seq=2 ttl=64 time=0.131 ms
64 bytes from 172.18.0.2: icmp_seq=3 ttl=64 time=0.079 ms
```
Вывод: В сети типа «bridge», созданной вручную, контейнеры могут общаться как по DNS-именам, так и по IP-адресам.
