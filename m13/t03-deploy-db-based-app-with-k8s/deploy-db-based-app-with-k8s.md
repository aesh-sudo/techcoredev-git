### Задача (Secret): Создать postgres-secret.yml (kind: Secret). ###

Создадим файл Секрета «postgres-secret.yml»:
```
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRES_PASSWORD: "mysecret"
```

```stringData:``` - специальное поле для указания данных в незакодированном (plain text) виде.

Отправим файл Секрета в «minikube» для обработки:
```bash
$ kubectl apply -f postgres-secret.yml
secret/postgres-secret created
```

При этом «k8s» создаст Секрет с именем ```postgres-secret```.<br>
Данные из ```stringData``` автоматически закодируются в «base64» и сохранятся в поле ```data```.

Убедимся, что Секрет создан:
```bash
$ kubectl get secrets
NAME              TYPE     DATA   AGE
postgres-secret   Opaque   1      119m
```

### Задача (ConfigMap): Создать postgres-configmap.yml (kind: ConfigMap). ###

Создадим файл «configmap» «postgres-configmap.yml»:
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-configmap
data:
  POSTGRES_DB: "devopsdb"
  POSTGRES_USER: "devops"
```

Отправим файл «configmap» в «minikube» для обработки:
```bash
$ kubectl apply -f postgres-configmap.yml
configmap/postgres-configmap created
```

Убедимся, что «configmap» создан:
```bash
$ kubectl get configmaps
NAME                 DATA   AGE
postgres-configmap   2      39s
```

### Задача (PVC): Создать postgres-pvc.yml (kind: PersistentVolumeClaim). ###

Создадим файл «PVC» «postgres-pvc.yml»:
```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```accessModes: [ReadWriteOnce]``` – диск может быть подключен для чтения и записи только одним узлом (Нодой) кластера одновременно.

```requests:``` - запрос ресурсов. Если на узле достаточно доступных ресурсов, контейнер может использовать больше ресурсов, чем указано.

Отправим файл «PVC» в «minikube» для обработки:
```bash
$ kubectl apply -f postgres-pvc.yml
persistentvolumeclaim/postgres-pvc created
```

Убедимся, что «PVC» создан:
```bash
$ kubectl get pvc
NAME           STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STOR-AGECLASS
   VOLUMEATTRIBUTESCLASS   AGE
postgres-pvc   Bound    pvc-d52a6ccb-9055-4891-9c3f-4d8e09fe93d1   1Gi        RWO            standard
   <unset>                 13s
```

### Задача (YAML - Deployment Postgres): Создать postgres-deployment.yml. ###
### Задача (Инъекция Config): В postgres-deployment.yml в spec.template.spec.containers добавить envFrom: ###
### Задача (Монтирование Volume): В postgres-deployment.yml "примонтировать" PVC. ###

Создадим файл Деплоймента «postgres-deployment.yml»:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres-db
  template:
    metadata:
      labels:
        app: postgres-db
    spec:
      containers:
      - name: postgres
        image: postgres:14-alpine
        ports:
        - containerPort: 5432
        envFrom:
        - configMapRef:
            name: postgres-configmap
        - secretRef:
            name: postgres-secret
        volumeMounts:
        - name: pg-data
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: pg-data
        persistentVolumeClaim:
          claimName: postgres-pvc
```

```selector``` и ```template.metadata.labels``` - метки, которые Деплоймент использует, чтобы понимать, какими Подами он должен управлять.

```envFrom``` – передача контейнеру данных переменных окружения:<br>
```configMapRef``` берет ```POSTGRES_DB``` и ```POSTGRES_USER``` из ```postgres-configmap```.<br>
```secretRef``` берет ```POSTGRES_PASSWORD``` из ```postgres-secret```.<br>
Внутри контейнера «Postrges» обнаружит переменные и будет настроен автоматически, при первом запуске.

```volumeMounts``` - контейнер берет Том с именем ```pg-data``` и подключает его к себе по пути, указанному в ```mountPath```.<br>
```/var/lib/postgresql/data``` – путь для хранения файлов БД (по умолчанию) в «Postgres».

```volumes``` – указывает на данные Тома ```pg-data```

Отправим файл Деплоймента в «minikube» для обработки:
```bash
$ kubectl apply -f postgres-deployment.yml
deployment.apps/postgres-deployment created
```
Проверим, что Под запустился:
```bash
$ kubectl get pods
NAME                                   READY   STATUS              RESTARTS   AGE
postgres-deployment-66bcbf9f44-2wnpz   0/1     ContainerCreating   0          31s

$ kubectl get pods
NAME                                   READY   STATUS    RESTARTS   AGE
postgres-deployment-66bcbf9f44-2wnpz   1/1     Running   0          77s
```

```STATUS: Running``` – признак того, что контейнер запустился.

Зайдем в контейнер, создадим в «Postgres» таблицу ```users``` и внесем в нее данные:
```bash
$ kubectl exec -it postgres-deployment-66bcbf9f44-2wnpz -- /bin/sh
/ #
/ # psql -U devops -d devopsdb
psql (14.23)
Type "help" for help.

devopsdb=# CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR(50), age INT);
CREATE TABLE
devopsdb=# INSERT INTO users (name, age) VALUES ('Алексей', 28);
INSERT 0 1
devopsdb=# SELECT * FROM users;
 id |  name   | age
----+---------+-----
  1 | Алексей |  28
(1 row)

devopsdb=# \dt
        List of relations
 Schema | Name  | Type  | Owner
--------+-------+-------+--------
 public | users | table | devops
(1 row)
```

```--``` - разделитель в команде ```kubectl```. Команды, указанные после него, выполняются уже в контейнере.

```psql -U devops -d devopsdb``` – запуск консоли БД.

### Задача (Service Postgres): Создать postgres-service.yml (type: ClusterIP, имя postgres-db). ###

Создадим файл Сервиса «postgres-service.yml»:
```
apiVersion: v1
kind: Service
metadata:
  name: postgres-db
spec:
  type: ClusterIP
  selector:
    app: postgres-db
  ports:
  - port: 5432
    targetPort: 5432
```

```metadata.name: postgres-db``` – DNS-имя внутри кластера.

```type: ClusterIP``` – тип Сервиса.<br>
```ClusterIP``` – Сервис доступен только внутри кластера. Для БД – самый оптимальный вариант.

```selector.app: postgres-db``` – метка Сервиса. Сервис будет направлять трафик на те Поды (описанные в Деплойменте), у которых аналогичная метка.

```port: 5432``` – порт, на котором Сервис слушает запросы.

```targetPort: 5432``` – порт, на который Сервис перенаправляет трафик внутри контейнера («Postgres» по умолчанию слушает порт 5432).

Отправим файл Сервиса в «minikube» для обработки:
```bash
$ kubectl apply -f postgres-service.yml
service/postgres-db created
```

Проверим, что Сервис создался:
```bash
$ kubectl get service
NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
postgres-db   ClusterIP   10.109.6.117   <none>        5432/TCP   29s
```

### Задача (Обновление my-app): В ConfigMap для my-app прописать DATABASE_URL (e.g., post-gresql://devops:mysecret@postgres-db:5432/devopsdb). Перезапустить my-app. ###

Переключим «Docker CLI» на использование Docker-демона внутри «minikube»:
```bash
$ eval $(minikube docker-env)
```

Теперь соберем образ приложения:
```bash
$ docker build -t my-app_13:k8s .
```

Проверим, появился ли образ:
```bash
$ docker images
IMAGE                                             ID             DISK USAGE   CONTENT SIZE   EXTRA
my-app_13:k8s                                     1be56d4cbe99        139MB             0B
```

Создадим Секрет для приложения «my-app_13:k8s»:
```
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secret
type: Opaque
stringData:
  DATABASE_URL: "postgresql://devops:mysecret@postgres-db:5432/devopsdb"
```

```postgresql://``` - протокол подключения.<br>
```devops``` - пользователь (из ```ConfigMap``` для «Postgres»).<br>
```mysecret``` - пароль (из Секрета для «Postgres»).<br>
```postgres-db``` - DNS-имя Сервиса для «Postgres».<br>
```5432``` - порт «Postgres».<br>
```devopsdb``` - имя БД (из ```ConfigMap``` для «Postgres»).

Отправим файл Секрета в «minikube» для обработки:
```bash
$ kubectl apply -f my-app-secret.yml
secret/my-app-secret created
```

Создадим Деплоймент для приложения «my-app_13:k8s»:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app_13:k8s
        ports:
        - containerPort: 5000
        envFrom:
        - secretRef:
            name: my-app-secret
```

Отправим файл Деплоймента в «minikube» для обработки:
```bash
$ kubectl apply -f my-app-deployment.yml
deployment.apps/my-app-deployment created
```

Создадим Сервис для приложения «my-app_13:k8s»:
```
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 5000
  type: NodePort
```

Отправим файл Сервиса в «minikube» для обработки:
```bash
$ kubectl apply -f my-app-service.yml
service/my-app-service created
```

Чтобы проверить работу приложения в браузере хоста, на котором развернута VM, необходимо выполнить команду:
```bash
nohup kubectl port-forward svc/my-app-service 8080:80 --address 0.0.0.0 > port-forward.log 2>&1 &
```

```nohub``` – поддерживает работу процесса даже после выхода из терминала.<br>
```&``` (в конце команды) – запуск процесса в фоновом режиме.<br>
```port-forward``` – команда создает безопасный туннель между локальным портом и портом ресурса в кластере.<br>
```svc/``` - путь к Сервису.<br>
```8080:80``` – маппинг портов. Локальный порт – ```8080```. Порт сервиса – ```80```.<br>
```--address 0.0.0.0``` – прием соединений на всех доступных сетевых интерфейсах.<br>
```> port-forward.log``` – перенаправление стандартного вывода в файл.

Чтобы удалить туннель, необходимо найти и убить его процесс:
```bash
ps aux | grep port-forward
kill <PID>
```

В браузере приложение будет доступно по адресу:
```
http://адрес_хоста:8080
```
