Создадим файл «postgres-statefulset.yml»:
```
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: pg                                1
spec:
  serviceName: postgres-headless          2
  replicas: 1                             3
  selector:
    matchLabels:
      app: postgres
  template:                               4
    metadata:
      labels:
        app: postgres                     5
    spec:
      containers:
        - name: postgres
          image: postgres:15
          ports:
            - containerPort: 5432         6
              name: postgres
          env:
            - name: POSTGRES_PASSWORD     7
              value: postgres
```

1 – имя Пода. Имена ```StatefulSet``` основаны на индексе, например, ```pg-0```, ```pg-1``` и т.д.<br>
2 - ссылка на ```Headless Service```, который будет создан в следующей задаче. Поду присваивается DNS-запись для обращения к нему по имени.<br>
3 – будет создана одна реплика (```pg-0```).<br>
4 – шаблон (параметры) для создания Пода.<br>
5 – метка Пода. Значение должно совпадать со значением в ```selector```. Таким образом ```StatefulSet``` находит принадлежащие ему Поды.<br>
6 - стандартный порт «Postgres».<br>
7 – пароль. «Postgres» требует задание пароля при старте, иначе контейнер будет остановлен с ошибкой. В проде для передачи пароля используют объект ```Secret```.

На данный момент внешнее хранилище данных не организовано, поэтому при перезапуске контейнера они пропадут.

Создадим Сервис ```Headless Service```, который даст Подам БД стабильные DNS-имена.<br>
Отличия обычного ```Service``` от ```Headless Service```:<br>
```Service```:
* Получает ```ClusterIP``` - один виртуальный IP-адрес на всю группу Подов. Виртуальный адрес ```Service``` внутри кластера (группы Нод).
* Является балансировщиком – запрос по IP-адресу автоматически распределяется на один из Подов.
* Поды идентичны, поэтому не имеет значения, какой Под будет обрабатывать запрос.

```Headless Service (clusterIP: None)```:
* Нет виртуального IP-адреса.
* ```DNS``` отдает IP-адреса Подов.
* Для Подов создаются персональные DNS-записи.

При этом реплика может обратиться к мастеру по имени напрямую, без участия балансировщика.

Создадим файл «postgres-headless-service.yml»:
```
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless     1
spec:
  clusterIP: None             2
  selector:
    app: postgres             3
  ports:
    - port: 5432
      targetPort: 5432
      name: postgres
```

1 – имя должно совпадать со значением параметра ```serviceName``` в ```StatefulSet```.<br>
2 – отключает виртуальный IP-адрес и включает режим ```headless```.<br>
3 – ```Headless Service``` взаимодействует с Подами, у которых есть аналогичная метка.

Секция ```ports``` в ```Headless Service``` носит информационный характер:<br>
```port``` – номер порта, под которым Сервис известен в кластере. Необходим для:
* Ответа в SRV-записи:<br>
Пример:<br>
Запрос:<br>
```_postgres._tcp.postgres-headless.default.svc.cluster.local```<br>
```_postgres``` - из ```name: postgres```.<br>
Ответ:<br>
```порт 5432, узел pg-0.postgres-headless...```

* Вывода и использования различными инструментами:
```kubectl get svc```

```targetPort``` – порт, который слушает контейнер (совпадает с ```containerPort``` в ```StatefulSet```).<br>
Узнать порт можно командой:
```bash
kubectl describe svc <имя_сервиса>
```
Значение будет в одноименной строке.

```name``` – имя порта. Необходимо для запроса в SRV-записи. Также позволяет ссылаться на порт по имени вместо цифры:
```
targetPort: postgres
```
вместо:
```
targetPort: 5432
```

```volumeClaimTemplates``` – шаблон, по которому ```StatefulSet``` создаст свой ```PVC``` для каждой реплики:
```
<имя_PVC = <имя_шаблона>-<имя_пода>
```

Свойства:
* Под монтирует только свой ```PVC```.
* При пересоздании Пода ```PVC``` остается и прикрепляется к тому же Поду.
* ```PVC``` из ```volumeClaimTemplates``` не удаляются при удалении ```StatefulSet``` - защита от случайной потери данных.
* Параметр ```storageClassName``` не указываем, чтобы применился стандартный для среды ```SC```.

Вынесем хранение данных наружу, в ```PVC```, который не исчезнет при перезапуске Пода.<br>
Опишем шаблон (```volumeClaimTemplates```), а «k8s» для каждой реплики автоматически создаст отдельный ```PVC```.<br>
Правило имени ```PVC```:
```
<имя шаблона>-<имя пода>
```
Дополним файл «postgres-statefulset.yml»:
```
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: pg
spec:
  serviceName: postgres-headless
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15
          ports:
            - containerPort: 5432
              name: postgres
          env:
            - name: POSTGRES_PASSWORD
              value: postgres
          volumeMounts:
            - name: data                              1
              mountPath: /var/lib/postgresql/data     2
  volumeClaimTemplates:
    - metadata:
        name: data                                    3
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

1 – имя должно совпадать с именем шаблона.<br>
2 – место монтирования диска в файловой системе Пода.<br>
3 – имя шаблона.

```volumeMounts``` – как использовать диск. Имя должно совпадать с именем из секции ```volumeClaimTemplates```.<br>
```volumeClaimTemplates``` – как создать диск.

Применим манифесты. Важен порядок применения – сначала ```Headless Service```, так как он нужен ```StatefulSet``` для ```DNS```.
```bash
$ kubectl apply -f postgres-headless-service.yml
service/postgres-headless created
$ kubectl apply -f postgres-statefulset.yml
statefulset.apps/pg created
```

Проверим, что ```StatefulSet``` запустил одну реплику ```pg```:
```bash
$ kubectl get statefulset pg
NAME   READY   AGE
pg     1/1     65s
```

Проверим статус Подов:
```bash
$ kubectl get pods
NAME   READY   STATUS    RESTARTS   AGE
pg-0   1/1     Running   0          5m32s
```

Проверим, что ```PVC``` связан (```bound```) с ```PV```:
```bash
$ kubectl get pvc
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS
   VOLUMEATTRIBUTESCLASS   AGE
data-pg-0   Bound    pvc-b08baa2e-1534-4756-89e3-0b8a97eddff1   1Gi        RWO            standard
   <unset>                 8m27s
```

Убедимся, что «Postgres» работает:
```bash
$ kubectl exec -it pg-0 -- psql -U postgres -c "SELECT 1 AS test;"
 test
------
    1
(1 row)
```
