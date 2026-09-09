На данный момент ```bitnami``` не распространяет репозитории бесплатно, поэтому перейдем на использование Чартов ```HelmForge```, которые распространяются так же, по стандарту ```OCI``` (как ```Docker Hub```).

Установим Чарт ```MySQL``` из репозитория ```Docker Hub```. Индивидуальные параметры установки приложения можно задать в специальном файле и указать его при установке.<br>
Файл ```my-mysql-values.yml```:
```
architecture: standalone

auth:
  rootPassword: "mysecret"
  database: "devopsdb"
  username: "devops"
  password: "mysecret"

standalone:
  persistence:
    enabled: true
    size: 1Gi
```

Имена параметров указаны разработчиком на странице продукта в ```Docker Hub``` или ```GitHub```.<br>
Например, в файле ```ConfigMap``` у нас были заданы параметры имени БД и пользователя.
```
data:
  MYSQL_DATABASE: "devopsdb"
  MYSQL_USER: "devops"
```

В файле настроек для установки через ```Helm``` мы указали:
```
auth:
  database: "devopsdb"
  username: "devops"
```

А нашли имена переменных мы на странице продукта. Например:<br>
```auth.database``` – имя создаваемой пользовательской базы данных.

Выполним установку:
```bash
helm install mysql oci://ghcr.io/helmforgedev/helm/mysql -f my-mysql-values.yml
```

В режиме реального времени проверим развертывание Пода:
```bash
$ kubectl get pods -w
NAME            READY   STATUS              RESTARTS   AGE
mysql-mysql-0   0/1     Pending             0          0s
mysql-mysql-0   0/1     ContainerCreating   0          1s
mysql-mysql-0   0/1     Running             0          3s
mysql-mysql-0   1/1     Running             0          32s
```

Аналогично установим ```MongoDB```.<br>
Создадим файл настроек ```my-mongo-values.yml```:
```
architecture: standalone

image:
  repository: docker.io/library/mongo
  tag: "4.4"

auth:
  enabled: true
  rootUser: root
  rootPassword: "mysecret"
  users:
    - username: devops
      password: mysecret
      database: devopsdb
      roles:
        - role: readWrite
          db: devopsdb

persistence:
  enabled: true
  size: 1Gi
```

```MongoDB``` версии ```5.0``` и выше требует ```AVX``` - набор инструкций для процессоров, который позволяет выполнять одну операцию над несколькими данными одновременно.<br>
Чтобы не использовать ```AVX```, будем использовать более раннюю версию ```MongoDB```:
```
image:
  repository: docker.io/library/mongo
  tag: "4.4"
```

Выполним установку:
```bash
helm install mongo oci://ghcr.io/helmforgedev/helm/mongodb -f my-mongo-values.yml
```

При наблюдении за Подами в реальном времени видим, что Под не готов:
```bash
$ kubectl get pods -w
NAME              READY   STATUS    RESTARTS       AGE
mongo-mongodb-0   0/1     Running   3 (2s ago)     15m
```

Проверим логи Пода (приложения):
```bash
$ kubectl logs mongo-mongodb-0
...
{"t":{"$date":"2026-09-09T20:48:31.214+00:00"},"s":"I",  "c":"NETWORK",  "id":23016,
   "ctx":"listener","msg":"Waiting for connections","attr":{"port":27017,"ssl":"off"}}
...
```

Судя по логам, БД запустилась и ждет подключений.

Проверим секцию ```Events``` (события) логов ```k8s``` (действия ```k8s``` с Подом):
```bash
$ kubectl describe pod mongo-mongodb-0
Events:
  Type     Reason     Age                    From             Message
  ----     ------     ----                   ----             -------
...
  Warning  Unhealthy  4m28s (x122 over 24m)  kubelet          spec.containers{mongod}:
                                                              Startup probe failed: sh: 2: mongosh: not found
```

Ошибка обозначает, что Чарт использует в проверках оболочку ```mongosh```, но в ```MongoDB``` она есть только начиная с версии ```5.0+```.<br>
Проверим настройки (```values```) Чарта. Это можно сделать тремя способами:<br>
Из ```Registry```:
```
helm show values <адрес_registry>
```

Из итоговых манифестов, сгенерированных ```Helm```:
```
helm get manifest <имя_манифеста_при_установке>
```

Из файла ```values.yaml``` на ```GitHub```.

Найдем секции, где встречается ```mongosh``` и вставим их в файл ```my-mongo-values.yml```, заменим ```mongosh``` на ```mongo```:
```
architecture: standalone

image:
  repository: docker.io/library/mongo
  tag: "4.4"

auth:
  enabled: true
  rootUser: root
  rootPassword: "mysecret"
  users:
    - username: devops
      password: mysecret
      database: devopsdb
      roles:
        - role: readWrite
          db: devopsdb

persistence:
  enabled: true
  size: 1Gi

# Переопределяем проверки: используем mongo (старый shell) вместо mongosh
livenessProbe:
  exec:
    command:
      - sh
      - -ec
      - |
        mongo --quiet --eval "db.adminCommand('ping')" -u "$MONGO_INITDB_ROOT_USERNAME"
          -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin
  initialDelaySeconds: 30
  periodSeconds: 20
  timeoutSeconds: 10
  failureThreshold: 6

readinessProbe:
  exec:
    command:
      - sh
      - -ec
      - |
        mongo --quiet --eval "db.adminCommand('ping')" -u "$MONGO_INITDB_ROOT_USERNAME"
          -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

startupProbe:
  exec:
    command:
      - sh
      - -ec
      - |
        mongo --quiet --eval "db.adminCommand('ping')" -u "$MONGO_INITDB_ROOT_USERNAME"
          -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 30
```
Тем самым мы переопределили необходимые нам места манифеста настроек.

Удалим сломанный релиз:
```bash
helm uninstall mongo
kubectl delete pvc datadir-mongo-mongodb-0 2>/dev/null || true
```

Выполним установку еще раз:
```bash
helm install mongo oci://ghcr.io/helmforgedev/helm/mongodb -f my-mongo-values.yml
```

В режиме реального времени проверим развертывание Пода:
```bash
$ kubectl get pods -w
NAME              READY   STATUS    RESTARTS      AGE
mongo-mongodb-0   0/1     Running   0             14s
mongo-mongodb-0   1/1     Running   0             22s
```

Проверим все запущенные Поды и диски к ним:
```bash
$ kubectl get pods
NAME              READY   STATUS    RESTARTS      AGE
mongo-mongodb-0   1/1     Running   0             8m44s
mysql-mysql-0     1/1     Running   1 (35m ago)   151m
pg-0              1/1     Running   7 (35m ago)   2d
pg-1              1/1     Running   5 (35m ago)   30h
pg-2              1/1     Running   5 (35m ago)   34h

$ kubectl get pvc
NAME                   STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS
   VOLUMEATTRIBUTESCLASS   AGE
data-mongo-mongodb-0   Bound    pvc-b90ae90d-23cd-4e1a-9ebc-0af63468f7aa   1Gi        RWO            standard
   <unset>                 6h56m
data-mysql-mysql-0     Bound    pvc-400adacf-2e1e-4cef-842a-c74a62d483fe   1Gi        RWO            standard
   <unset>                 7h28m
data-pg-0              Bound    pvc-b08baa2e-1534-4756-89e3-0b8a97eddff1   1Gi        RWO            standard
   <unset>                 2d
data-pg-1              Bound    pvc-99bde255-f01f-4153-a164-f6c00ad6bd3d   1Gi        RWO            standard
   <unset>                 34h
data-pg-2              Bound    pvc-9aea53e1-561a-424b-950e-1189a4e10caf   1Gi        RWO            standard
   <unset>                 34h
```

Посмотрим Поды ```StatefulSet```:
```bash
$ kubectl get statefulset
NAME            READY   AGE
mongo-mongodb   1/1     11m
mysql-mysql     1/1     153m
pg              3/3     2d
```
