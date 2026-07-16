### Задача (Установка Helm): Установить Helm. ###

Установим ```Helm``` с помощью скрипта, который представлен на официальном сайте. Команды установки описаны в документации.

Проверим установку:
```bash
$ helm version
version.BuildInfo{Version:"v4.2.3", GitCommit:"43e8b7feece8beb0fcba47059ec9b522fd929a64",
 GitTreeState:"clean", GoVersion:"go1.26.5", KubeClientVersion:"v1.36"}
```

### Задача (Helm Repo): Добавить репозиторий: helm repo add bitnami https://charts.bitnami.com/bitnami. ###
### Задача (Helm Install): Удалить наш Postgres (из М13). Установить его через Helm: helm install my-pg bit-nami/postgresql. ###

Политика распространения репозиториев компании «bitnami» изменилась. Теперь они распространяются по стандарту «OCI» (как «Docker Hub»).

Установим Чарт «PostgreSQL» из репозитория «Docker Hub». Индивидуальные параметры установки приложения можно задать в специальном файле и указать его при установке.<br>
Файл «my-postgres-values.yml»:
```
auth:
  postgresPassword: "mysecret"
  database: "devopsdb"
  username: "devops"
  password: "mysecret"
primary:
  persistence:
    size: 1Gi
```

Имена параметров указаны разработчиком на странице продукта в «Docker Hub» или «GitHub».
Например, в файле «ConfigMap» у нас были заданы параметры имени БД и пользователя.
```
data:
  POSTGRES_DB: "devopsdb"
  POSTGRES_USER: "devops"
```

В файле настроек для установки через «Helm» мы указали:
```
auth:
  database: "devopsdb"
  username: "devops"
```

А нашли имена переменных мы на странице продукта. Например:<br>
```auth.database``` – имя создаваемой пользовательской базы данных.

Выполним установку:
```bash
helm install my-pg oci://registry-1.docker.io/bitnamicharts/postgresql -f my-postgres-values.yml
```

Посмотрим Сервис «PostgreSQL»:
```bash
$ kubectl get service
NAME                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
my-pg-postgresql      ClusterIP   10.101.98.253   <none>        5432/TCP   3m3s
my-pg-postgresql-hl   ClusterIP   None            <none>        5432/TCP   3m3s
```

Сервис называется ```my-pg-postgresql```, поэтому в файле Секрета приложения ```my-app``` изменим путь для соединения с БД:
```
DATABASE_URL: "postgresql://devops:mysecret@my-pg-postgresql:5432/devopsdb"
```

Напомню, что в прошлой задаче Секрет, который мы создавали вручную, назывался ```postgres-db```.

Подключимся к Поду с БД и внесем в нее запись:
```bash
$ kubectl get pods
NAME                 READY   STATUS    RESTARTS   AGE
my-pg-postgresql-0   1/1     Running   0          12m

$ kubectl exec -it my-pg-postgresql-0 -- psql -U devops -d devopsdb
Password for user devops:
psql (18.4)
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

Применим файлы приложения «my-app» к кластеру:
```bash
kubectl apply -f my-app-secret.yml
kubectl apply -f my-app-deployment.yml
kubectl apply -f my-app-service.yml
kubectl apply -f app-ingress.yml
```

Проверим работу приложения:
```bash
$ curl http://my-app.local/app

    <h1>Docker-контейнер</h1>
    <h2>Первая запись в БД:</h2>
    <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
        <p><strong>Имя:</strong> Алексей</p>
        <p><strong>Возраст:</strong> 28 лет</p>
    </div>
```
