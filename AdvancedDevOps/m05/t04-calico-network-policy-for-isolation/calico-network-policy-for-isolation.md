По умолчанию в ```k8s``` все Поды видят друг друга. ```NetworkPolicy``` меняет модель на «белый список» (```whitelist```) для выбранных Подов.<br>
Запрет выполняется как ```DROP``` - пакеты отбрасываются без каких-либо уведомлений. У клиента выполнение запроса продолжается до таймаута.

Создадим манифест для примера – файл «netpol-lab.yml»:
```yaml
# БД "Postgres" с меткой "app=db"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          env:
            - name: POSTGRES_PASSWORD
              value: secret
          ports:
            - containerPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: db-svc
spec:
  selector:
    app: db
  ports:
    - port: 5432
      targetPort: 5432
---
# Легальный клиент: "busybox" с меткой "app=api"
apiVersion: v1
kind: Pod
metadata:
  name: api
  labels:
    app: api
spec:
  containers:
    - name: box
      image: busybox:1.36
      command: ["sleep", "3600"]
---
# Хакер: "busybox" с меткой "app=hacker"
apiVersion: v1
kind: Pod
metadata:
  name: hacker-pod
  labels:
    app: hacker
spec:
  containers:
    - name: box
      image: busybox:1.36
      command: ["sleep", "3600"]
```

Применим манифест:
```bash
$ kubectl apply -f netpol-lab.yml
deployment.apps/db created
service/db-svc created
pod/api created
pod/hacker-pod created
```

Следить за запуском Подов можно в режиме реального времени (покажем только результат):
```bash
$ kubectl get pods -w
NAME                            READY   STATUS              RESTARTS   AGE
api                             1/1     Running             0          81s
db-95d7985b-zw6j5               1/1     Running             0          117s
hacker-pod                      1/1     Running             0          118s
```

Протестируем подключение к Сервису ```db-svc```:
```bash
$ kubectl exec api -- nc -z -w 3 db-svc 5432 && echo "CONNECTED" || echo "DENIED"
CONNECTED
$ kubectl exec hacker-pod -- nc -z -w 3 db-svc 5432 && echo "CONNECTED" || echo "DENIED"
CONNECTED
```

```nc``` – утилита для работы с сетевыми соединениями. Возвращает ```0``` – успех, ```не 0``` – неудача.<br>
```-z``` – режим проверки порта без отправки данных.<br>
```-w 3``` – таймаут 3 секунды. Если за это время соединение не будет установлено, то команда завершится с ошибкой.

Создадим ```NetworkPolicy``` - файл ```db-networkpolicy.yml```:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-allow-api
spec:
  podSelector:
    matchLabels:
      app: db
  policyTypes:
    - Ingress
  ingress:
    - from:
      - podSelector:
          matchLabels:
            app: api
```

```podSelector``` – Поды, к которым будет применяться сетевая политика. Для выбора Подов используются метки (```labels```).
Синтаксис:
```yaml
podSelector:
  matchLabels:
    имя_метки: значение
    имя_метки_1: значение_1
    ...
    имя_метки_n: значение_n
```

Важно также учитывать пространство имен. ```podSelector``` в ```from``` без ```namespaceSelector``` ищет Поды только в том же пространстве имен, что и сама политика. Чтобы указать Поды из другого пространства имен, необходимо комбинировать:
```yaml
from:
- namespaceSelector:
    matchLabels:
      env: prod
  podSelector:
    matchLabels:
      app: frontend
```

```namespaceSelector``` и ```podSelector``` в одном элементе, значит соединяются по ```AND```. Читается как: Пространство имен ```prod``` и Под ```frontend``` в нем.

```policyTypes``` – направление трафика, к которому будет применена сетевая политика:
* ```Ingress``` – входящий трафик (значение по умолчанию).
* ```Egress``` – исходящий трафик.<br>
Также можно указать оба направления сразу.<br>
Если поле ```policyTypes``` не указано, то ```k8s``` определяет значение типа сетевой политики по наличию блоков ```ingress/egress```. В примере тип сетевой политики по умолчанию был бы ```Ingress```. Но лучше указывать явно.

```ingress: from``` – разрешенный источник трафика. Источником может быть:
* ```ipBlock.cidr``` - диапазон IP-адресов в нотации ```CIDR```.
* ```namespaceSelector``` - селектор по меткам пространства имен.
* ```podSelector``` - селектор по меткам Подов.

В примере будет разрешен входящий трафик к Подам с меткой ```app: db``` только от Подов с меткой ```app: api```.

Если порты (```ports```) не указаны, то от указанного источника разрешается трафик на все порты.

Политики складываются аддитивно – разрешено то, что разрешено в одной из сетевых политик.

Применим и проверим сетевые политики:
```bash
$ kubectl apply -f db-networkpolicy.yml
networkpolicy.networking.k8s.io/db-allow-api created

$ kubectl get networkpolicy
NAME           POD-SELECTOR   AGE
db-allow-api   app=db         43s
```

Проверим работу сетевых политик:
```bash
$ kubectl exec api -- nc -z -w 3 db-svc 5432 && echo "CONNECTED" || echo "DENIED"
CONNECTED
$ kubectl exec hacker-pod -- nc -z -w 3 db-svc 5432 && echo "CONNECTED" || echo "DENIED"
command terminated with exit code 1
DENIED
```

Как видит сетевую политику плагин ```Calico```:
```bash
$ kubectl describe networkpolicy db-allow-api
Name:         db-allow-api
Namespace:    default
Created on:   2026-09-15 20:18:59 +0000 UTC
Labels:       <none>
Annotations:  <none>
Spec:
  PodSelector:     app=db
  Allowing ingress traffic:
    To Port: <any> (traffic allowed to all ports)
    From:
      PodSelector: app=api
  Not affecting egress traffic
  Policy Types: Ingress
```
