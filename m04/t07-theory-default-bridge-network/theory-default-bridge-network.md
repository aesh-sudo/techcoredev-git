Создадим два контейнера:
```bash
$ docker run --rm -d --name net_bridge_default_1 ubuntu sleep 10000
d2a0f8cd40ebdf60d1ed910569c4a2430c86ea27b14fde41395afa1f032f5f1a
$ docker run --rm -d --name net_bridge_default_2 ubuntu sleep 10000
0673de4ec18d7737a1c2a76b05078d4dfbdc71b909c14cc8f4c5ce5630b1a8d3
```

Узнаем их IP-адреса:
```bash
$ docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' net_bridge_default_1
172.17.0.2
$ docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' net_bridge_default_2
172.17.0.3
```

Зайдем в один из контейнеров и попробуем пропинговать второй по IP-адресу и по имени:
```bash
$ docker exec -it net_bridge_default_1 /bin/bash
# apt-get update && apt-get install -y iputils-ping
# ping 172.17.0.3
PING 172.17.0.3 (172.17.0.3) 56(84) bytes of data.
64 bytes from 172.17.0.3: icmp_seq=1 ttl=64 time=0.652 ms
64 bytes from 172.17.0.3: icmp_seq=2 ttl=64 time=0.116 ms
64 bytes from 172.17.0.3: icmp_seq=3 ttl=64 time=0.073 ms

# ping net_bridge_default_2
ping: net_bridge_default_2: Name or service not known
```
Вывод:<br>
В сети типа «bridge», созданной по умолчанию, контейнеры могут общаться между собой только по IP-адресам, но не могут общаться по DNS-именам.
