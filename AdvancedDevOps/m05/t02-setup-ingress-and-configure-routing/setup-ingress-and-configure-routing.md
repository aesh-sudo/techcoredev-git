В ```minikube``` ```Ingress``` не включен по умолчанию. Его можно активировать как встроенное дополнение (```addon```):
```bash
minikube addons enable ingress
```

Проверим, что ```Ingress Controller``` запустился:
```bash
$ kubectl get pods -n ingress-nginx
NAME                                        READY   STATUS      RESTARTS   AGE
ingress-nginx-admission-create-8hlc5        0/1     Completed   0          3m27s
ingress-nginx-admission-patch-2gbch         0/1     Completed   0          3m26s
ingress-nginx-controller-596f8778bc-nh6vc   1/1     Running     0          3m27s
```

Посмотрим Сервисы ```Ingress```:
```bash
$ kubectl get svc -n ingress-nginx
NAME                                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)
   AGE
ingress-nginx-controller             NodePort    10.101.68.19   <none>        80:31361/TCP,443:32172/TCP
   8m30s
ingress-nginx-controller-admission   ClusterIP   10.106.74.20   <none>        443/TCP
   8m30s
```

```ingress-nginx-controller (NodePort)``` – точка входа для внешнего трафика. Слушает порты ```80 HTTP``` и ```443 HTTPS```, которые проброшены на Ноду как ```31361/32172```. Соответственно, в ```minikube``` на этот Сервис направлены порты ```80/443```, поэтому внешние тесты делаются через:
```bash
curl $(minikube ip)/...
```

```ingress-nginx-controller-admission (ClusterIP)``` – внутренний Сервис. Через него ```k8s``` создает/изменяет конфигурации объектов ```Ingress```.

Проверим статус аддона:
```bash
$ minikube addons list | grep ingress
│         ADDON NAME          │ PROFILE  │   STATUS   │               MAINTAINER               │
│ ingress                     │ minikube │ enabled    │ Kubernetes                             │
│ ingress-dns                 │ minikube │ disabled   │ minikube                               │
```

##########

Для решения нам понадобятся:
* Два тестовых приложения, которые будут возвращать разный текст, чтобы убедиться, что маршрутизация работает.
* Два Сервиса (```ClusterIP```) – внутренние точки входа.
* Один ```Ingress``` с правилами ```path-based``` маршрутизации.

```hashicorp/http-echo``` – образ, который будем использовать для тестовых приложений. Возвращает заданный текст на любой HTTP-запрос.

Создадим манифест ```book-service``` - файл ```book-service.yml```:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: book-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: book-service
  template:
    metadata:
      labels:
        app: book-service
    spec:
      containers:
        - name: book-service
          image: hashicorp/http-echo:latest
          args:
            - "-text=book-service response"
          ports:
            - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: book-service
spec:
  type: ClusterIP
  selector:
    app: book-service
  ports:
    - port: 80
      targetPort: 5678
```

Создадим манифест ```user-service``` - файл ```user-service.yml```:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
        - name: user-service
          image: hashicorp/http-echo:latest
          args:
            - "-text=user-service response"
          ports:
            - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  type: ClusterIP
  selector:
    app: user-service
  ports:
    - port: 80
      targetPort: 5678
```

Создадим ```Ingress``` с ```path-based``` правилами – файл ```path-ingress.yml```:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /api/books
            pathType: Prefix
            backend:
              service:
                name: book-service
                port:
                  number: 80
          - path: /api/users
            pathType: Prefix
            backend:
              service:
                name: user-service
                port:
                  number: 80
```

```ingressClassName: nginx``` – связь ```Ingress``` с ```Ingress Controller```. Данный ```Ingress``` будет обрабатываться контроллером ```nginx```.

```annotations: rewrite-target: /``` - убирает ```/api/books``` или ```/api/users``` из ```URL``` перед отправкой в Сервис. Например, без этого Сервис ```book-service``` получил бы запрос ```/api/books```, а он отвечает только на ```/```.

```path: /api/books``` – путь, который ```Ingress``` принимает в обработку.<br>
```path: /api/users``` – путь, который ```Ingress``` принимает в обработку.

```pathType: Prefix``` – путь запроса, принимаемого ```Ingress``` в обработку, должен иметь префикс ```/api/books*``` или ```/api/users*```.

```backend.service.name``` – точка направления запроса.

Применим манифесты:
```bash
$ kubectl apply -f book-service.yml
deployment.apps/book-service created
service/book-service created

kubectl apply -f user-service.yml
deployment.apps/user-service created
service/user-service created

kubectl apply -f path-ingress.yml
ingress.networking.k8s.io/path-ingress created
```

Посмотрим созданные Поды:
```bash
$ kubectl get pods
NAME                            READY   STATUS    RESTARTS   AGE
book-service-5856859b6f-kfjq8   1/1     Running   0          30s
user-service-69d9fdc879-p6p6j   1/1     Running   0          30s
```

Посмотрим созданный ```Ingress```:
```bash
$ kubectl get ingress
NAME          CLASS   HOSTS   ADDRESS        PORTS   AGE
path-ingress   nginx   *       192.168.49.2   80      67s
```

```ADDRESS``` – если поле пустое, значит контроллер еще не принял правила.<br>
```192.168.49.2``` – IP-адрес ```minikube```:
```bash
$ minikube ip
192.168.49.2
```

Проверим доступ к приложениям:
```bash
$ curl $(minikube ip)/api/books
book-service response

$ curl $(minikube ip)/api/users
user-service response

# для /api/other маршрутизации нет
$ curl -I $(minikube ip)/api/other
HTTP/1.1 404 Not Found
Date: Fri, 11 Sep 2026 17:56:22 GMT
Content-Type: text/html
Content-Length: 146
Connection: keep-alive
```

##########

Когда браузер или ```curl``` обращается к ```http://домен```, он отправляет HTTP-заголовок:
```
GET / HTTP/1.1
Host: books.my-app.local   # этот заголовок читает Ingress
```

```Ingress Controller``` читает ```Host``` и сверяет его с правилами:
```
Host: books.my-app.local   book-service
Host: users.my-app.local   user-service
```

Значение файла ```hosts```:<br>
Он выполняет роль DNS-сервера, в котором мы пропишем, что эти домены соответствуют IP-адресу ```minikube```.
```bash
$ minikube ip
192.168.49.2
```

В файл ```/etc/hosts``` запишем:
```
192.168.49.2 books.my-app.local
192.168.49.2 users.my-app.local
```

Проверим резолв:
```bash
$ getent hosts books.my-app.local
192.168.49.2    books.my-app.local
$ getent hosts users.my-app.local
192.168.49.2    users.my-app.local
```

Создадим ```Ingress``` с ```host-based``` правилами – файл ```host-ingress.yml```:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: books.my-app.local         # домен 1
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: book-service
                port:
                  number: 80
    - host: users.my-app.local         # домен 2
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: user-service
                port:
                  number: 80
```

```path: /``` - выполняется фильтрация по домену и для направления к Сервису не учитывается путь внутри.

Применим манифест:
```bash
$ kubectl apply -f host-ingress.yml
ingress.networking.k8s.io/host-ingress created
```

Проверим созданные ```Ingress```:
```bash
$ kubectl get ingress
NAME           CLASS   HOSTS                                   ADDRESS        PORTS   AGE
host-ingress   nginx   books.my-app.local,users.my-app.local   192.168.49.2   80      50m
path-ingress   nginx   *                                       192.168.49.2   80      6m22s
```

В колонке ```HOSTS``` у ```path-based``` стоит ```*``` (любой хост), а у ```host-based``` - конкретные домены.

Проверим доступ к приложениям:
```bash
$ curl http://books.my-app.local/
book-service response
$ curl http://users.my-app.local/
user-service response
```

Проверим доступ чужого домена на тот же IP-адрес:
```bash
$ curl -H "Host: unknown.local" http://$(minikube ip)/
<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
```

Домен не описан в правилах, ```Ingress Controller``` не может его обработать.

IP-адрес нужен только для доставки запроса до ```Ingress Controller``` (hosts-файл - локальная замена ```DNS``` для получения IP-адреса). Само решение по маршрутизации контроллер принимает по заголовку ```Host``` внутри HTTP-запроса: запросы с одинаковым ```Host``` дадут одинаковый результат, независимо от способа получения IP-адреса.

Можно обойтись без hosts-файла, подделав заголовок вручную:
```bash
$ curl -H "Host: books.my-app.local" http://$(minikube ip)/
book-service response

$ curl -H "Host: users.my-app.local" http://$(minikube ip)/
user-service response
```
