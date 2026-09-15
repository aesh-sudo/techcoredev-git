Сетевая модель ```k8s```:
* Каждый Под имеет свой IP-адрес.
* Поды могут общаться друг с другом, даже если они расположены на разных Нодах.

Сам ```k8s``` не реализует сеть. Существует спецификация ```CNI (Container Network Interface)``` - контракт: при создании/удалении Пода ```kubelet``` вызывает внешний плагин, который создает/удаляет сеть Пода.

Некоторые реализации плагина:<br>
```Flannel``` – простой учебный.<br>
Соединение: оверлей ```VXLAN```.<br>
```NetworkPolicy```: НЕТ.
<br><br>

```Calico``` – production-стандарт. Используется в промышленных кластерах. Надежный, масштабируемый, гибкий.<br>
Соединение: ```BGP/VXLAN```.<br>
```NetworkPolicy```: ДА.
<br><br>

```WeaveNet``` – аналогичен ```Flannel```, но с возможностью настройки ```NetworkPolicy```.<br>
Соединение: оверлей ```Weave```.<br>
```NetworkPolicy```: ДА.
<br><br>

```Cilium``` – мощный ```CNI``` для высоконагруженных систем, ```service mesh``` и сложных сценариев безопасности.<br>
Соединение: ```eBPF```. Использует современные возможности ядра ```Linux``` для маршрутизации и фильтрации. Это обеспечивает высокую производительность и низкую задержку.<br>
```NetworkPolicy```: ДА. Позволяет создавать политики как на основе IP/портов (```L3/L4```), так и на уровне приложений (```L7```).

Соединение Нод – технология, с помощью которой пакеты данных передаются между Нодами кластера.<br>
Оверлей ```VXLAN``` – инкапсуляция трафика. Работает поверх обычной сети и не требует настройки маршрутизации на роутерах.<br>
```BGP``` – динамическая маршрутизация. Ноды обмениваются информацией о местонахождении Подов на уровне ```L3``` (сетевой). Быстрее, но сложнее в настройке.<br>
```eBPF``` – технология ядра ```Linux```. Позволяет быстро обрабатывать пакеты, минуя сетевой стек.<br>
```NetworkPolicy``` - поддержка сетевых политик (правил файрвола между Подами).

Механика работы плагина:<br>
```kubelet``` читает конфиг из ```/etc/cni/net.d/``` (первый файл по алфавиту).<br>
По списку ```plugins``` конфига вызывает бинарники из ```/opt/cni/bin```.

По умолчанию в ```minikube``` нет отдельного плагина с Подами-агентами. Используется статический конфиг с мостом.<br>
Плагины нужны для передачи трафика между Нодами. В ```minikube``` одна Нода и локальные Поды, поэтому достаточно моста.

Конфиг ```CNI``` (первый файл по алфавиту):
```bash
$ minikube ssh -- sudo cat /etc/cni/net.d/1-k8s.conflist

{
  "cniVersion": "0.4.0",
  "name": "bridge",
  "plugins": [
    {
      "type": "bridge",
      "bridge": "bridge",
      "addIf": "true",
      "isDefaultGateway": true,
      "forceAddress": false,
      "ipMasq": true,
      "hairpinMode": true,
      "ipam": {
          "type": "host-local",
          "subnet": "10.244.0.0/16"
      }
    },
    {
      "type": "portmap",
      "capabilities": {
          "portMappings": true
      }
    },
    {
       "type": "firewall"
    }
  ]
}
```

```ipam.subnet: 10.244.0.0/16``` – подсеть, из которой Подам раздаются IP-адреса.<br>
```ipMasq: true``` – наружу трафик Пода маскируется под IP-адрес Ноды. Поэтому ```10.244.x.x``` - внутренняя сеть кластера.<br>
```firewall``` – только служебные правила файрвола. Мостовой ```CNI``` не поддерживает механизм ```NetworkPolicy```. ```k8s``` применит манифест ```NetworkPolicy```, но CNI-плагин не умеет выполнять его политики.

Инструменты плагина:
```bash
$ minikube ssh -- ls -l /opt/cni/bin
total 96124
-rw-r--r-- 1 root root    11357 Dec  9  2025 LICENSE
-rw-r--r-- 1 root root     2343 Dec  9  2025 README.md
-rwxr-xr-x 1 root root  5042758 Dec  9  2025 bandwidth
-rwxr-xr-x 1 root root  5694787 Dec  9  2025 bridge
-rwxr-xr-x 1 root root 13722883 Dec  9  2025 dhcp
-rwxr-xr-x 1 root root  5251429 Dec  9  2025 dummy
-rwxr-xr-x 1 root root  5702489 Dec  9  2025 firewall
-rwxr-xr-x 1 root root  5160095 Dec  9  2025 host-device
-rwxr-xr-x 1 root root  4350898 Dec  9  2025 host-local
-rwxr-xr-x 1 root root  5278618 Dec  9  2025 ipvlan
-rwxr-xr-x 1 root root  4302030 Dec  9  2025 loopback
-rwxr-xr-x 1 root root  5307015 Dec  9  2025 macvlan
-rwxr-xr-x 1 root root  5108286 Dec  9  2025 portmap
-rwxr-xr-x 1 root root  5475550 Dec  9  2025 ptp
-rwxr-xr-x 1 root root  4525802 Dec  9  2025 sbr
-rwxr-xr-x 1 root root  3776700 Dec  9  2025 static
-rwxr-xr-x 1 root root  5331503 Dec  9  2025 tap
-rwxr-xr-x 1 root root  4389108 Dec  9  2025 tuning
-rwxr-xr-x 1 root root  5267823 Dec  9  2025 vlan
-rwxr-xr-x 1 root root  4685300 Dec  9  2025 vrf
```

Агенты внешних плагинов представлены в виде Подов – по одному на каждую Ноду. За этим в ```k8s``` следит контроллер ```DaemonSet```.

Пересоздадим кластер ```minikube``` с указанием внешнего плагина ```Calico```:
```bash
minikube delete
minikube start --cni=calico
```

Проверим Поды ```CNI```:
```bash
$ kubectl get pods -n kube-system | grep calico
calico-kube-controllers-565c89d6df-wkvt5   1/1     Running   0          57m
calico-node-tgz6j                          1/1     Running   0          57m
```

```calico-node-xxxxx``` – агент ```CNI```, который создается на каждой Ноде кластера, и выполняет работу по реализации сети ```Calico```.<br>
```calico-kube-controllers``` – управляющий Под. Один на кластер. Следит за тем, чтобы правила, которые задаются в ```k8s``` (например, через ```NetworkPolicy```), корректно отражались на работе сети ```Calico```.

Проверим конфиг ```CNI``` - теперь он ```Calico```:
```bash
$ minikube ssh -- sudo cat /etc/cni/net.d/10-calico.conflist
{
  "name": "k8s-pod-network",
  "cniVersion": "0.3.1",
  "plugins": [
    {
      "type": "calico",
      "log_level": "info",
      "log_file_path": "/var/log/calico/cni/cni.log",
      "datastore_type": "kubernetes",
      "nodename": "minikube",
      "mtu": 0,
      "ipam": {
          "type": "calico-ipam"
      },
      "policy": {
          "type": "k8s"
      },
      "kubernetes": {
          "kubeconfig": "/etc/cni/net.d/calico-kubeconfig"
      }
    },
    {
      "type": "portmap",
      "snat": true,
      "capabilities": {"portMappings": true}
    }
  ]
}
```

```"policy": { "type": "k8s" }``` - поддержка сетевых политик (правил файрвола между Подами).

Появился интерфейс ```tunl0``` - IPIP-туннель для трафика между Нодами:
```bash
$ minikube ssh -- ip addr | grep -A 2 tunl0
2: tunl0@NONE: <NOARP,UP,LOWER_UP> mtu 1480 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ipip 0.0.0.0 brd 0.0.0.0
    inet 10.244.120.64/32 scope global tunl0
       valid_lft forever preferred_lft forever
3: eth0@if32: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default
```

##########

```CoreDNS``` – DNS-сервер, работающий внутри кластера, в пространстве имен (```namespace```) ```kube-system```.<br>
```kube-dns``` – сервис ```ClusterIP```, который указывает на Поды ```CoreDNS```. Все Поды кластера настроены использовать его IP-адрес как адрес DNS-сервера.

Принцип работы:<br>
Под A хочет обратиться к Сервису ```postgres-db```:<br>
1. Под A читает у себя файл ```/etc/resolv.conf``` и находит IP-адрес DNS-сервера, например, ```nameserver 10.96.0.10```.<br>
2. Под A отправляет DNS-запрос: ```postgres-db```.<br>
3. Запрос идет на ```10.96.0.10``` - Сервис ```kube-dns``` и перенаправляется в Под с ```CoreDNS```.<br>
4. ```CoreDNS``` отвечает: ```postgres-db = 10.96.45.123```.<br>
5. Под A подключается к ```10.96.45.123:5432```.

Посмотрим Под ```CoreDNS```:
```bash
$ kubectl get pods -n kube-system | grep coredns
NAME                                       READY   STATUS    RESTARTS   AGE
coredns-7d764666f9-7dtvb                   1/1     Running   0          111m
```

Посмотрим Сервис ```kube-dns```:
```bash
$ kubectl get svc -n kube-system | grep dns
NAME       TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
kube-dns   ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   10h
```

```CLUSTER-IP: 10.96.0.10``` – ```nameserver```, который прописан в файле ```/etc/resolv.conf``` каждого Пода.

Возьмем Под ```book-service``` из задачи 4.<br>
Так как он создан на основе минимального образа ```hashicorp/http-echo:latest```, то в нем нет командной оболочки.<br>
Используем команду, которая добавит в Под временный контейнер с нужными инструментами:
```bash
$ kubectl debug -it book-service-5856859b6f-wgtfj --image=busybox --target=book-service
/ #
```

```--target=book-service``` – подключит отладочный контейнер к пространству имен процессов целевого контейнера, что позволит видеть его процессы. Отладочный контейнер также видит ```pod-level``` файлы. Они одинаковы для всех контейнеров Пода.

Посмотрим DNS-настройки:
```bash
/ # cat /etc/resolv.conf
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

```nameserver 10.96.0.10``` – IP-адрес Сервиса ```kube-dns``` (```CoreDNS```). Все DNS-запросы идут сюда.<br>
```search default.svc.cluster.local svc.cluster.local cluster.local``` – суффиксы для коротких имен. Например, если приложение пришлет ```postgres-db```, то система попробует DNS-имена с суффиксами из списка.<br>
```options ndots:5``` – если в имени меньше пяти точек, сначала пробовать с суффиксами.

Проверим резолв IP-адреса Пода c приложением ```user-service```:
```bash
/ # nslookup user-service
Server:         10.96.0.10
Address:        10.96.0.10:53

Name:   user-service.default.svc.cluster.local
Address: 10.105.140.242
```

Проверим:
```bash
$ kubectl get svc user-service
NAME           TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
user-service   ClusterIP   10.105.140.242   <none>        80/TCP    11h
```

Видим, что IP-адрес найден верно.

Проверим резолв по полному имени:
```bash
/ # nslookup user-service.default.svc.cluster.local
Server:         10.96.0.10
Address:        10.96.0.10:53

Name:   user-service.default.svc.cluster.local
Address: 10.105.140.242
```

Результат тот же, но без search-суффиксов (не указаны в предыдущем выводе резолва).

Проверим резолв несуществующего Сервиса:
```bash
/ # nslookup fake-service
Server:         10.96.0.10
Address:        10.96.0.10:53

** server can't find fake-service.default.svc.cluster.local: NXDOMAIN
** server can't find fake-service.svc.cluster.local: NXDOMAIN
** server can't find fake-service.svc.cluster.local: NXDOMAIN
** server can't find fake-service.cluster.local: NXDOMAIN
** server can't find fake-service.default.svc.cluster.local: NXDOMAIN
** server can't find fake-service.cluster.local: NXDOMAIN
```

```CoreDNS``` не нашел Сервиса с заданным именем.
