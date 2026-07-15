### Задача (Включение Ingress): Включить Ingress Controller в Minikube: minikube addons enable ingress. ###

В «minikube» ```Ingress``` не включен по умолчанию. Его можно активировать как встроенное дополнение (addon).:
```bash
minikube addons enable ingress
```

Проверим, что ```Ingress Controller``` запустился:
```bash
$ kubectl get pods -n ingress-nginx
NAME                                        READY   STATUS      RESTARTS   AGE
ingress-nginx-admission-create-zgbkq        0/1     Completed   0          6m56s
ingress-nginx-admission-patch-jfwg6         0/1     Completed   1          6m56s
ingress-nginx-controller-596f8778bc-v2qgv   1/1     Running     0          6m56s
```

```-n (--namespace)``` – параметр для указания пространства имен, поды которого необходимо вывести.

### Задача (YAML - Ingress): Создать app-ingress.yml (kind: Ingress, apiVersion: networking.k8s.io/v1). ###
### Задача (Правила Ingress): Описать spec.rules. ###

```Ingress Controller``` запущен. Теперь ему надо дать инструкцию с правилами, по которым он должен работать.

Создадим файл Ингресса «app-ingress.yml»:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /app
        pathType: Prefix
        backend:
          service:
            name: my-app-service
            port:
              number: 80
```

```apiVersion: networking.k8s.io/v1``` – стабильная версия API для работы с ```Ingress``` в «k8s».<br>
```rules``` – раздел списка правил маршрутизации. В задаче одно правило, которое будет применяться ко всем запросам, приходящим на IP-адрес кластера.<br>
```annotations``` – указывает контроллеру, что внутри «minikube» необходимо переписать запрос с ```/app``` на ```/```, так как приложение «app.py» слушает корневой путь:
```python
@app.route('/')
```
```path: /app``` – путь, на который будет срабатывать правило перенаправления.<br>
```pathType: Prefix``` – правило будет срабатывать для всех путей, начинающихся с ```/app```.<br>
```backend.service``` – куда перенаправлять отобранный трафик. В задаче ссылаемся на Сервис ```my-app-service```, созданный ранее, и его порт.

### Задача (Тест Ingress): kubectl apply -f app-ingress.yml. Узнать IP Minikube (minikube ip). ###

Отправим файл Ингресса в «minikube» для обработки:
```bash
$ kubectl apply -f app-ingress.yml
ingress.networking.k8s.io/my-app-ingress created
```

Изменим файл Сервиса «my-app-service.yml»:
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
  type: ClusterIP
```

```type: ClusterIP``` – тип Сервиса.<br>
```ClusterIP``` – Сервис доступен только внутри кластера.

Применим все манифесты приложения:
```bash
kubectl apply -f postgres-secret.yml \
				-f postgres-configmap.yml \
				-f postgres-pvc.yml \
				-f postgres-deployment.yml \
				-f postgres-service.yml \
				-f my-app-secret.yml \
				-f my-app-deployment.yml \
				-f my-app-service.yml \
				-f app-ingress.yml
```

Проверим, что Поды запустились:
```bash
$ kubectl get pods
NAME                                   READY   STATUS    RESTARTS   AGE
my-app-deployment-7dfc8d9c4c-dm62n     1/1     Running   0          21s
postgres-deployment-66bcbf9f44-rl4x9   1/1     Running   0          21s
```

Зайдем в контейнер, создадим в «Postgres» таблицу ```users``` и внесем в нее данные:
```bash
$ kubectl exec -it postgres-deployment-66bcbf9f44-rl4x9 -- /bin/sh
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

Проверим результат:
```bash
$ curl http://$(minikube ip)/app

    <h1>Docker-контейнер</h1>
    <h2>Первая запись в БД:</h2>
    <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
        <p><strong>Имя:</strong> Алексей</p>
        <p><strong>Возраст:</strong> 28 лет</p>
    </div>
```

### Задача (Ingress (Host-based)): Настроить DNS. Добавить $(minikube ip) my-app.local в /etc/hosts (или C:\...). Изменить Ingress.yml, добавив host: my-app.local. ###

Необходимо, чтобы приложение отвечало только тогда, когда к нему обращаются по имени ```my-app.local```.

Изменим файл Ингресса «app-ingress.yml». Добавим строку с именем обращения ```host: my-app.local```:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: my-app.local
    http:
      paths:
      - path: /app
        pathType: Prefix
        backend:
          service:
            name: my-app-service
            port:
              number: 80
```

Применим изменения манифеста Ингресса:
```bash
$ kubectl apply -f app-ingress.yml
ingress.networking.k8s.io/my-app-ingress configured
```

На VM в файл ```/etc/hosts``` запишем IP-адрес и имя, по которому теперь можно обратиться к приложению (DNS-запись):
```bash
$ echo "$(minikube ip) my-app.local" | sudo tee -a /etc/hosts
192.168.49.2 my-app.local
```

Проверим результат:
```bash
$ curl http://my-app.local/app

    <h1>Docker-контейнер</h1>
    <h2>Первая запись в БД:</h2>
    <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
        <p><strong>Имя:</strong> Алексей</p>
        <p><strong>Возраст:</strong> 28 лет</p>
    </div>
```
