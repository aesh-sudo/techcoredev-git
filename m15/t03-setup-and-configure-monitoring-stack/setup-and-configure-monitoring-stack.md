### Задача (Helm Install Prometheus): Установить Prometheus Stack. ###

Добавим индекс репозитория «prometheus-community» в локальный «Helm»:
```bash
$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
"prometheus-community" has been added to your repositories
```

Обновим список репозиториев:
```bash
$ helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈Happy Helming!⎈
```

Установим стек мониторинга:
```bash
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

```-n monitoring``` – пространство имен, в которое будет установлен Чарт.<br>
```--create-namespace``` – если пространства имен нет, то оно будет создано автоматически.

Проверим выполнение команды:
```bash
$ kubectl get pods -n monitoring
NAME                                                     READY   STATUS    RESTARTS   AGE
alertmanager-prometheus-kube-prometheus-alertmanager-0   2/2     Running   0          12m
prometheus-grafana-755d5b7fd8-q9kqx                      3/3     Running   0          13m
prometheus-kube-prometheus-operator-6cf54bfcf5-9bv8k     1/1     Running   0          13m
prometheus-kube-state-metrics-848b96f989-czc7v           1/1     Running   0          13m
prometheus-prometheus-kube-prometheus-prometheus-0       2/2     Running   0          12m
prometheus-prometheus-node-exporter-v7tpj                1/1     Running   0          13m
```

### Задача (Доступ к Prometheus): kubectl port-forward -n monitoring svc/prometheus-k8s 9090. ###

Проверим список Сервисов:
```bash
$ kubectl get svc -n monitoring
NAME                                      TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
alertmanager-operated                     ClusterIP   None            <none>        9093/TCP,9094/TCP,9094/UDP   36m
prometheus-grafana                        ClusterIP   10.98.3.169     <none>        80/TCP                       36m
prometheus-kube-prometheus-alertmanager   ClusterIP   10.106.87.71    <none>        9093/TCP,8080/TCP            36m
prometheus-kube-prometheus-operator       ClusterIP   10.109.159.43   <none>        443/TCP                      36m
prometheus-kube-prometheus-prometheus     ClusterIP   10.99.185.125   <none>        9090/TCP,8080/TCP            36m
prometheus-kube-state-metrics             ClusterIP   10.104.155.70   <none>        8080/TCP                     36m
prometheus-operated                       ClusterIP   None            <none>        9090/TCP                     36m
prometheus-prometheus-node-exporter       ClusterIP   10.111.174.78   <none>        9100/TCP                     36m
```

Чтобы открыть «Prometheus» в браузере хоста создадим туннель к Сервису «Prometheus»:
```bash
nohup kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090
 --address 0.0.0.0 > port-forward.log 2>&1 &
```

Чтобы открыть приложение в браузере хоста:
```
http://ip_адрес_хоста:9090/
```

### Задача (Доступ к Grafana): kubectl port-forward -n monitoring svc/prometheus-grafana 3000. ###

Узнаем пароль администратора «Grafana», который был назначен по умолчанию при установке стека мониторинга:
```bash
kubectl get secret --namespace monitoring -l app.kubernetes.io/component=admin-secret
 -o jsonpath="{.items[0].data.admin-password}" | base64 --decode ; echo
```

Команда получения пароля «Grafana» будет указана в информации при установке стека мониторинга.

### Задача (Изучение Grafana): Зайти в Grafana. Открыть Dashboards. Найти дашборды, которые kube-prometheus-stack установил автоматически (e.g., "K8s / Compute Resources / Cluster"). ###

Чтобы открыть «Grafana» в браузере хоста создадим туннель к Сервису «Grafana»:
```bash
export POD_NAME=$(kubectl --namespace monitoring get pod
 -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=prometheus" -oname)

nohup kubectl --namespace monitoring port-forward $POD_NAME 3000
 --address 0.0.0.0 > port-forward.log 2>&1 &
```

Команда создания туннеля к Сервису «Grafana» будет указана в информации при установке стека мониторинга.

Логин администратора у «Grafana» - ```admin```.

Чтобы в «Grafana» найти графики «CPU/Memory» кластера «minikube» необходимо выбрать меню:
```
Dashboards - Kubernetes / Compute Resources / Cluster
```

### Задача (App-side): "Выставить" метрики из my-app. ###

Добавим в файл зависимостей приложения ```my-app``` (```requirements.txt```) библиотеку:
```
prometheus-client==0.25.0
```

Модифицируем файл приложения ```app.py``` - импортируем библиотеку, создадим счетчик запросов и новый маршрут:
```
/metrics
```
```python
app.py:
from flask import Flask, Response
import psycopg2
import os
from prometheus_client import Counter, generate_latest                                               1

app = Flask(__name__)

# Счетчик вызовов главной страницы
REQUEST_COUNT = Counter('app_hello_requests_total', 'Total number of requests to the main page')     2

@app.route('/')
def hello():
    # Увеличиваем счетчик на 1 при каждом заходе на страницу
    REQUEST_COUNT.inc()                                                                              3

    # Подключение к БД
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    # Получение первой записи
    cur.execute('SELECT name, age FROM users ORDER BY id LIMIT 1')
    name, age = cur.fetchone()

    cur.close()
    conn.close()

    return f'''
    <h1>Docker-контейнер</h1>
    <h2>Первая запись в БД:</h2>
    <div style="background: #f0f0f0; padding: 20px; border-radius: 10px;">
        <p><strong>Имя:</strong> {name}</p>
        <p><strong>Возраст:</strong> {age} лет</p>
    </div>
    '''

# Маршрут для метрик "Prometheus"                                                                    4
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain; charset=utf-8')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

1:<br>
```Counter``` – метрика. Представляет из себя счетчик, который только увеличивается. При перезапуске приложения сбрасывается в ноль.<br>
```generate_latest``` – функция-утилита для вывода метрик. Генерирует текстовые данные со всеми текущими значениями метрик в формате, понятном для сервера «Prometheus».

2:<br>
```Counter()``` – вызов конструктора класса ```Counter```, который создает новый объект метрики типа «счетчик».<br>
```app_hello_requests_total``` – имя метрики для отображения в «Prometheus». Суффикс ```_total``` обязателен, он сигнализирует, что метрика монотонно возрастает.<br>
```Total number of requests to the main page``` – комментарий по предназначению метрики.

3:<br>
```.inc()``` – метод инкремента (увеличения) счетчика.

4:<br>
```@app.route('/metrics')``` – декоратор «Flask». Привязывает функцию к URL-адресу ```/metrics```.<br>
Действие: при переходе по адресу ```http://адрес_сайта/metrics```, «Flask» вызывает функцию ```metrics()```.<br>
```return Response(generate_latest(), mimetype='text/plain; charset=utf-8')``` – функция собирает все зарегистрированные метрики в текущем процессе и форматирует их в текстовый формат «Prometheus».

Переключим «Docker CLI» на использование Docker-демона внутри «Minikube VM»:
```bash
eval $(minikube docker-env)
```

Пересоберем образ:
```bash
docker build -t my-app_15:k8s .
```

Применим изменения манифеста Деплоймента приложения:
```bash
$ kubectl apply -f my-app-deployment.yml
deployment.apps/my-app-deployment configured
```

Проверим, что Под с приложением перезапустился:
```bash
$ kubectl get pods -l app=my-app
NAME                                 READY   STATUS    RESTARTS   AGE
my-app-deployment-6444474fb6-pczhr   1/1     Running   0          6m12s
```

Проверим результат, создав туннель в Под приложения ```my-app```:
```bash
$ kubectl port-forward deployment/my-app-deployment 5000:5000 --address 0.0.0.0
```

```deployment/my-app-deployment``` – имя Деплоймента, в отличие от Подов, у которых в конце прибавляется хеш, не меняется. ```kubectl``` находит Деплоймент с нужным именем и пробрасывает порт в случайный Под, управляемый этим Деплойментом.<br>
Аналогично можно пробрасывать порты от Сервисов:
```bash
kubectl port-forward svc/my-app-service 5000:80
```

Результат можно увидеть по адресу:
```
http://ip_адрес_хоста:5000/metrics
```

В результате собранные метрики будут представлены в текстовом формате.

### Задача (YAML - ServiceMonitor): Создать app-monitor.yml (kind: ServiceMonitor). ###

Изменим файл Сервиса приложения «my-app-service.yml»:
```
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
  labels:
    app: my-app            1
spec:
  selector:
    app: my-app
  ports:
  - name: http             2
    port: 80
    targetPort: 5000
  type: ClusterIP
```

```1``` – добавили метку для Сервиса, по которой «ServiceMonitor» найдет Сервис.<br>
```2``` – «ServiceMonitor» выполняет поиск порта по имени.

Применим изменения файла Сервиса «my-app-service.yml» приложения ```my-app``` к кластеру:
```bash
$ kubectl apply -f my-app-service.yml
service/my-app-service configured
```

Создадим файл «ServiceMonitor» - «app-monitor.yml»:
```
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app-monitor
  namespace: monitoring
  labels:
    app: my-app
    release: prometheus
spec:
  selector:
    matchLabels:
      app: my-app
  namespaceSelector:
    matchNames:
    - default
  endpoints:
  - port: http
    interval: 15s
```

```metadata.namespace: monitoring``` – «ServiceMonitor» должен быть в том же пространстве имен, что и «Prometheus».<br>
```metadata.labels.release: prometheus``` – метка для того, чтобы «Prometheus» собирал метрики с этого «Service-Monitor».<br>
```spec.selector.matchLabels.app: my-app``` – метка, по которой «ServiceMonitor» найдет Сервис приложения.<br>
```spec.namespaceSelector.matchNames: default``` – поиск Сервисов в пространстве имен ```default```.<br>
```port: http``` – имя порта для поиска в Сервисе.<br>
```interval: 15s``` – интервал сбора метрик. Каждые 15 секунд.

Применим файл «ServiceMonitor» - «app-monitor.yml» к кластеру:
```bash
$ kubectl apply -f app-monitor.yml
servicemonitor.monitoring.coreos.com/my-app-monitor created
```

Проверим, что «ServiceMonitor» создан:
```bash
$ kubectl get servicemonitor -n monitoring
NAME                                                 AGE
my-app-monitor                                       2m40s
```

### Задача (Проверка): Зайти в UI Prometheus -> Status -> Targets. ###

Сначала метрики можно посмотреть в самом Поде приложения, создав туннель в Под приложения ```my-app```:
```bash
kubectl port-forward deployment/my-app-deployment 5000:5000 --address 0.0.0.0
```

И перейдя по адресу:
```
http://ip_адрес_хоста:5000/metrics
```

В «Prometheus» перейдем в меню «Status – Target health»:<br>
Метрика:
```
serviceMonitor/monitoring/my-app-monitor/0
```
должна быть в статусе (```State```) - ```UP```

### Задача (Логи): Основы логирования. ###

```kubectl logs``` – команда для просмотра логов контейнеров в Подах.<br>
```kubectl logs deployment/my-app-deployment``` – просмотр логов всех Подов указанного Деплоймента.<br>
```kubectl logs -f deployment/my-app-deployment``` – аналогично, но в реальном времени.

Также можно посмотреть логи Подов каких-либо Деплойментов.<br>
Пример:
```bash
$ kubectl -n monitoring get deployment
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
prometheus-grafana                    1/1     1            1           13h
prometheus-kube-prometheus-operator   1/1     1            1           13h
prometheus-kube-state-metrics         1/1     1            1           13h
$ kubectl logs -n monitoring deployment/prometheus-grafana
```
