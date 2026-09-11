Поды в ```k8s``` эфемерны, их IP-адреса могут меняться. Клиенту необходимо предоставить универсальный способ обращения к Подам.<br>
```Service``` – стабильная точка входа с постоянным IP-адресом и DNS-именем. Сервис следит за принадлежащими ему Подами с помощью меток (```selector```) и направляет на них трафик.

Сервисы бывают трех типов:<br>
1\. ```ClusterIP```.<br>
Тип Сервиса, установленный по умолчанию. Используется только внутри кластера. Доступ извне (из интернета или с хоста) закрыт.<br>
Используется для БД, внутренних ```API```, которые не должны быть видны снаружи и микросервисов, которые должны общаться только друг с другом.

Пример:<br>
Создадим файл Сервиса ```postgres-db-service.yml```:
```
apiVersion: v1
kind: Service
metadata:
  name: postgres-db
spec:
  type: ClusterIP     # значение по умолчанию, можно не указывать
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```

```postgres-db:5432``` - DNS-имя, по которому можно обратиться к Сервису внутри кластера.

Создадим и проверим Сервис в кластере ```k8s```:
```bash
$ kubectl apply -f postgres-db-service.yml
service/postgres-db created

$ kubectl get svc postgres-db
NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
postgres-db   ClusterIP   10.96.146.71   <none>        5432/TCP   58s
```

```EXTERNAL-IP: <none>``` - доступа снаружи нет.
<br><br>

2\. ```NodePort``` (для разработки).<br>
Сервис состоит из ```ClusterIP``` (внутри кластера) и порта на каждой Ноде (```NodePort```). Доступен снаружи через IP-адрес любой Ноды:
```
<NodeIP>:<NodePort>
```

Используется в основном при разработке и тестировании – доступ к сервису снаружи, минуя балансировщик. Также используется в ```minikube```, локальных кластерах без ```LoadBalancer``` и в простых приложениях.

Пример:<br>
Создадим файл Сервиса ```web-app-service.yml```:
```
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80             # порт внутри кластера
      targetPort: 8080     # порт в контейнере
      nodePort: 30080      # порт на ноде (опционально, 30000-32767)
```

```web-app:80``` - DNS-имя, по которому можно обратиться к Сервису внутри кластера.<br>
```<NodeIP>:30080``` – обращение к Сервису снаружи.

Создадим и проверим Сервис в кластере ```k8s```:
```bash
$ kubectl apply -f web-app-service.yml
service/web-app created

$ kubectl get svc web-app
NAME      TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
web-app   NodePort   10.104.122.112   <none>        80:30080/TCP   10s
```

```80:30080``` – это ```ClusterIP-порт:NodePort```.

Доступ из браузера:<br>
Получить IP-адрес ```minikube```:
```bash
$ minikube ip
192.168.49.2
```
Открыть в браузере:
```
http://192.168.49.2:30080
```

Ограничения:
* Нежелательно использовать в ```production``` - порт может конфликтовать и нет балансировки.<br>
* Если Нода выйдет из строя, то Сервис будет недоступен. Нужен внешний балансировщик.
<br><br>

3\. ```LoadBalancer``` (для ```production``` в облаке).<br>
Сервис состоит из ```ClusterIP```, ```NodePort``` и внешнего IP-адреса от провайдера. Провайдер создает балансировщик нагрузки и присваивает ему внешний IP-адрес.

Используется в основном когда нужен стабильный внешний IP-адрес и/или автоматическая балансировка между Нодами.

Пример:<br>
Создадим файл Сервиса ```api-gateway-service.yml```:
```
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
spec:
  type: LoadBalancer
  selector:
    app: api
  ports:
    - port: 443
      targetPort: 8443
```

```api-gateway:443``` - DNS-имя, по которому можно обратиться к Сервису внутри кластера.<br>
```<External-IP>:443``` – обращение к Сервису снаружи.

Создадим и проверим Сервис в кластере ```k8s```:
```bash
$ kubectl apply -f api-gateway-service.yml
service/api-gateway created

$ kubectl get svc api-gateway
NAME          TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)         AGE
api-gateway   LoadBalancer   10.109.39.152   <pending>     443:31378/TCP   52s
```

```EXTERNAL-IP = <pending>``` - в «minikube» по умолчанию нет контроллера для выделения внешних IP-адресов.

##########

```Service``` – работает на транспортном уровне (```L4```) модели ```OSI```:
* Работает только с IP-адресами и портами.
* Не работает с содержимым трафика.

Логика работы – трафик пришел на определенный порт:
```
ClusterIP:port
```
Его надо передать на любой Под кластера, у которого есть метка, совпадающая с меткой Сервиса.

Но, если приложение состоит из нескольких микросервисов, то возникают проблемы:<br>
```NodePort```:<br>
Микросервисы имеют одинаковый IP-адрес, но разные порты.

```LoadBalancer```:<br>
Каждый микросервис имеет свой IP-адрес и ```LoadBalancer```.

Недостатки:
* Клиент должен знать порт необходимого микросервиса:<br>
```app.com:30001/books```
* Каждый «LoadBalancer» в облаке оплачивается отдельно.
* Нет маршрутизации по ```URL```.
* HTTP-сертификат придется настраивать для каждого входа отдельно.
<br><br>

```Ingress``` - работает на транспортном уровне (```L7```) модели ```OSI```.<br>
Читает содержимое HTTP-запроса:<br>
```URL``` – одинаковый домен и порт, но разные пути ведут к разным приложениям:
```
example.com/api/orders   сервис orders
example.com/api/users    сервис users
example.com/             фронтенд
```

Заголовок ```host``` - разные домены могут вести на один и тот же IP-адрес балансировщика, но ```Ingress``` разводит их по разным микросервисам.
```
shop.example.com   сервис магазина
blog.example.com   сервис блога
```

Метод – анализ методов (```GET```, ```POST```, ```PUT``` и т.д.) для принятия решений по перенаправлению трафика.

Способы маршрутизации:<br>
```Path-based``` – по пути в ```URL```:
```
app.com/api/books   book-service
app.com/api/users   user-service
```

```Host-based``` – по заголовку ```host``` (домену):
```
books.my-app.local   book-service
users.my-app.local   user-service
```

Пример yaml-файла ```Ingress```:
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
    - http:
        paths:
          - path: /api/books          # если URL начинается с /api/books
            pathType: Prefix
            backend:
              service:
                name: book-service    # отправить в этот Service
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

```Ingress``` направляет трафик в ```Service``` с определенными настройками, а ```Service``` уже перенаправляет его по Подам.

```Ingress``` - декларативный набор правил.<br>
```Ingress Controller``` - отдельное приложение в кластере, которое исполняет правила ```Ingress```.
