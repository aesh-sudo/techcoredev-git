В ```GitLab``` создадим новый пустой проект с именем ```app-7-2```.<br>
Создадим ```GitLab K8s Agent```. Для этого зайдем в проект и в меню:<br>
```Operate – Kubernetes clusters```<br>
Нажмем на ```Connect a cluster```. В открывшемся окне введем имя создаваемого агента:<br>
```minikube-agent```<br>
и нажмем ```Create and register```. Откроется окно с инструкцией по установке агента через ```Helm```, и его токеном:
```bash
helm repo add gitlab https://charts.gitlab.io
helm repo update
helm upgrade --install minikube-agent gitlab/gitlab-agent \
    --namespace gitlab-agent-minikube-agent \
    --create-namespace \
    --set image.tag=v19.4.0 \
    --set config.token=токен_агента \
    --set config.kasAddress=ws://gitlab.aesh.com:/-/kubernetes-agent/
```

Перед выполнением необходимо проверить и дополнить команду данными проекта. В примере ```kasAddress``` необходимо дополнить значением порта, на котором находится ```GitLab```:<br>
```--set config.kasAddress=ws://gitlab.aesh.com:8929/-/kubernetes-agent/```

```ws://``` - если ```GitLab``` доступен по ```HTTP```, то используется WebSocket‑протокол.<br>
```wss://``` - если ```GitLab``` доступен по ```HTTPS```, то используется WebSocket‑протокол поверх ```TLS```.

Проверим Поды агента:
```bash
$ kubectl get pods -n gitlab-agent-minikube-agent
NAME                                             READY   STATUS    RESTARTS   AGE
minikube-agent-gitlab-agent-v2-cf457cf8f-2jghg   1/1     Running   0          40s
minikube-agent-gitlab-agent-v2-cf457cf8f-b5q4h   1/1     Running   0          40s
```

Запишем разрешение (резолв) адреса ```GitLab``` на хосте (```/etc/hosts```):<br>
```192.168.1.121 gitlab.aesh.com```<br>
Когда агент, работающий в ```minikube```, пытается подключиться к домену ```gitlab.aesh.com```, он сначала ищет ip-адрес этого домена на хосте, а именно в файле ```/etc/hosts```, а затем обращается в интернет.

Перезапустим Поды агента:
```bash
$ kubectl rollout restart deployment -n gitlab-agent-minikube-agent
deployment.apps/minikube-agent-gitlab-agent-v2 restarted
```
Уже запущенные Поды могут хранить информацию о том, что не нашли ip-адрес домена ```gitlab.aesh.com```, в кэше, а их перезапуск повторяет алгоритм поиска разрешения домена.

Также проверим логи установки:
```bash
$ kubectl logs -n gitlab-agent-minikube-agent -l app.kubernetes.io/name=gitlab-agent
{"time":"2026-10-13T05:21:36.418357808Z","level":"INFO","msg":"Flux could not be detected or the Agent is
 missing RBAC, skipping module. A restart is required for this to be checked again","mod_name":"flux"}
{"time":"2026-10-13T05:21:36.422731951Z","level":"INFO","msg":"Starting","mod_name":"agent_registrar"}
{"time":"2026-10-13T05:21:36.425528604Z","level":"INFO","msg":"Starting","mod_name":"agent2kas_tunnel"}
{"time":"2026-10-13T05:21:36.425704138Z","level":"INFO","msg":"Starting","mod_name":"google_profiler"}
{"time":"2026-10-13T05:21:36.425727914Z","level":"INFO","msg":"Starting","mod_name":"observability"}
{"time":"2026-10-13T05:21:36.427793956Z","level":"INFO","msg":"Observability endpoint is up",
"mod_name":"observability","net_network":"tcp","net_address":"[::]:8080"}
{"time":"2026-10-13T05:21:36.49393077Z","level":"INFO","msg":"Attempting to acquire leader
 lease...","agent_key":"agentk:1","lock":"gitlab-agent-minikube-agent/agent-1-lock"}
{"time":"2026-10-13T05:21:23.71799976Z","level":"INFO","msg":"Starting","mod_name":"google_profiler"}
{"time":"2026-10-13T05:21:23.719473543Z","level":"INFO","msg":"Starting","mod_name":"observability"}
{"time":"2026-10-13T05:21:23.720382758Z","level":"INFO","msg":"Starting","mod_name":"agent_registrar"}
{"time":"2026-10-13T05:21:23.72070357Z","level":"INFO","msg":"Observability endpoint is up",
"mod_name":"observability","net_network":"tcp","net_address":"[::]:8080"}
{"time":"2026-10-13T05:21:23.720961932Z","level":"INFO","msg":"Starting","mod_name":"agent2kas_tunnel"}
{"time":"2026-10-13T05:21:23.82967024Z","level":"INFO","msg":"Attempting to acquire leader
 lease...","agent_key":"agentk:1","lock":"gitlab-agent-minikube-agent/agent-1-lock"}
{"time":"2026-10-13T05:21:47.122806531Z","level":"INFO","msg":"Successfully acquired lease",
"agent_key":"agentk:1","lock":"gitlab-agent-minikube-agent/agent-1-lock"}
{"time":"2026-10-13T05:21:47.128310572Z","level":"INFO","msg":"Starting",
"mod_name":"starboard_vulnerability","agent_key":"agentk:1"}
{"time":"2026-10-13T05:21:47.128901987Z","level":"INFO","msg":"Starting",
"mod_name":"remote_development","agent_key":"agentk:1"}
{"time":"2026-10-13T05:21:47.131138607Z","level":"INFO","msg":"Event occurred","agent_key":"agentk:1",
"object":{"name":"agent-1-lock","namespace":"gitlab-agent-minikube-agent"},"fieldPath":"","kind":"Lease",
"apiVersion":"coordination.k8s.io/v1","type":"Normal","reason":"LeaderElection",
"message":"minikube-agent-gitlab-agent-v2-6c4bfc989-kwvzx became leader"}
```

Видим, что ошибок нет, агент установлен корректно.

Вернемся в ```GitLab```, на страницу создания агента. Статус соединения созданного агента ```minikube-agent``` должен стать ```Connected```.

########## 2

Для выполнения пайплайна проекта зарегистрируем для него ```runner```:
```bash
docker exec -it gitlab-runner gitlab-runner register \
  --url http://gitlab.aesh.com:8929 \
  --registration-token токен_полученный_при_создании_раннера_в_GitLab \
  --executor docker \
  --docker-image alpine:latest \
  --description "app-7-2-runner" \
  --docker-network-mode gitlab-install_default
```

Структура проекта:
```
~/gitlab-projects/app-7-2$ tree -a -I ".git"
.
├── docker-compose.yml
├── .gitlab-ci.yml
└── k8s
    └── deployment.yml
```

Файл ```deployment.yml```:
```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-7-2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: app-7-2
  template:
    metadata:
      labels:
        app: app-7-2
    spec:
      containers:
        - name: app-7-2
          image: nginx:alpine
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 80
```

Файл ```.gitlab-ci.yml```:
```yml
stages:
  - deploy

deploy:
  stage: deploy
  image: gcr.io/google.com/cloudsdktool/google-cloud-cli:latest
  script:
    # Переключаем контекст (это дает kubectl токен доступа)
    - kubectl config use-context root/app-7-2:minikube-agent

    # Проверяем ответ кластера
    - kubectl cluster-info

    # Применяем манифест
    - kubectl apply -f k8s/deployment.yml

    # Проверяем результат
    - kubectl get pods -l app=app-7-2
  environment:
    name: production
    kubernetes:
      namespace: default
```

Перейдем в ```GitLab``` и попробуем выполнить пайплайн.<br>
Пайплайн не выполнился. Ошибка:
```
$ kubectl cluster-info
E1019 11:07:55.331668      17 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: the server has asked for the client to provide credentials"
...
E1019 11:07:55.401069      17 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: the server has asked for the client to provide credentials"
error: You must be logged in to the server (the server has asked for the client to provide credentials)
To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

```GitLab``` требует ```HTTPS``` для аутентификации ```CI_JOB_TOKEN``` через ```Kubernetes Agent```. Переведем ```GitLab``` на ```HTTPS```.<br>
Создадим SSL-сертификаты с ```SAN```:
```bash
mkdir -p ~/gitlab-ssl
cd ~/gitlab-ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout gitlab.aesh.com.key \
  -out gitlab.aesh.com.crt \
  -subj "/CN=gitlab.aesh.com" \
  -addext "subjectAltName=DNS:gitlab.aesh.com"

chmod 644 gitlab.aesh.com.crt
chmod 600 gitlab.aesh.com.key
```

Обновим файл ```docker-compose.yml``` для ```GitLab``` - добавим монтирование каталога с сертификатами и поменяем адрес на использование ```HTTPS```:
```yml
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: gitlab
    restart: always
    hostname: 'gitlab.aesh.com'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'https://gitlab.aesh.com:8929'
        gitlab_rails['gitlab_shell_ssh_port'] = 10022

        # HTTPS настройки
        nginx['ssl_certificate'] = "/etc/gitlab/ssl/gitlab.aesh.com.crt"
        nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/gitlab.aesh.com.key"

        # Отключаем HTTP/2 (критично для WebSockets)
        gitlab_rails['nginx']['http2_enabled'] = false

        # Настройка WORKHORSE И KAS
        gitlab_workhorse['listen_network'] = "tcp"
        gitlab_workhorse['listen_addr'] = "127.0.0.1:8181"
        gitlab_kas['gitlab_address'] = 'http://127.0.0.1:8181'
        gitlab_kas['external_url'] = 'wss://gitlab.aesh.com:8929/-/kubernetes-agent/'
    ports:
      - '8929:8929'
      - '10022:22'
    volumes:
      - 'gitlab_config:/etc/gitlab'
      - 'gitlab_logs:/var/log/gitlab'
      - 'gitlab_data:/var/opt/gitlab'
      - '~/gitlab-ssl:/etc/gitlab/ssl'
    shm_size: '256m'
volumes:
  gitlab_config:
  gitlab_logs:
  gitlab_data:
```

```GITLAB_OMNIBUS_CONFIG```<br>
Переменная окружения, используемая при развертывании ```GitLab``` в ```Docker```. Задает настройки конфигурации в момент запуска контейнера, не изменяя конфигурационный файл.

```gitlab_rails['nginx']['http2_enabled'] = false```<br>
```Nginx``` – компонент ```GitLab```, который принимает все внешние запросы.<br>
В ```Nginx``` отключаем протокол ```HTTP/2```.<br>
```WebSocket``` – постоянное соединение поверх ```HTTP```, которое после рукопожатия становится двунаправленным каналом.<br>
В ```HTTP/2``` соединения мультиплексируются (много потоков в одном TCP-соединении). Браузер или агент при этом не может корректно переключиться на ```WebSocket```.<br>
```GitLab Kubernetes Agent (KAS)``` работает через ```WebSocket (wss://)```.

```gitlab_workhorse['listen_network'] = "tcp"```<br>
```gitlab_workhorse['listen_addr'] = "127.0.0.1:8181"```<br>
```Workhorse``` - компонент ```GitLab```, который выполняет основную работу.<br>
```listen_network = "tcp"``` – ```Workhorse``` слушает TCP-сокет, а не Unix-сокет, который используется по умолчанию.<br>
```listen_addr = "127.0.0.1:8181"``` – ```Workhorse``` слушает только локально (```127.0.0.1```), на порту ```8181```.<br>
Таким образом, внутренние компоненты ```GitLab``` могут обращаться к ```Workhorse``` через ```http://127.0.0.1:8181```.<br>
```Workhorse``` при этом не должен быть доступен снаружи.

```gitlab_kas['gitlab_address'] = 'http://127.0.0.1:8181'```<br>
```GitLab Kubernetes Agent Server (KAS)``` – сервис, который принимает WebSocker-соединения от агентов. В примере - от minikube-агента.<br>
Когда необходимо обратиться к ```GitLab```, ```KAS``` использует внутренний адрес ```Workhorse```.

```gitlab_kas['external_url'] = 'wss://gitlab.aesh.com:8929/-/kubernetes-agent/'```<br>
```wss://(WebSocket Secure)``` - шифрованное соединение поверх ```TLS```.<br>
```/-/kubernetes-agent/``` - внутренний путь, по которому ```GitLab KAS``` принимает соединения от агентов. Это «точка входа» для k8s‑агентов.

Принцип взаимодействия:
* Агент (в ```minikube```) подключается по ```wss://gitlab.aesh.com:8929/-/kubernetes-agent/```.
* ```Nginx``` принимает соединение и корректно обрабатывает ```WebSocket```, так как ```HTTP/2``` отключен.
* ```Nginx``` проксирует соединение в ```KAS```.
* ```KAS``` может обращаться к ```GitLab``` через ```http://127.0.0.1:8181``` (```Workhorse```).

Аналогичный адрес указывается в конфигурации агента.

Перезапустим ```GitLab``` - команды выполняем в том же каталоге, в котором находится файл ```docker-compose.yml``` с конфигурацией ```GitLab```:
```bash
docker compose down
docker compose up -d
```

При подключении по ```HTTPS``` агент проверяет, подписан ли сертификат официальным доверенным центром. Если самоподписанный сертификат поместить в ```Secret``` и смонтировать его в контейнер агента, то он будет доверять этому сертификату.

Создадим ```Secret```:
```bash
$ kubectl create secret generic gitlab-ca-cert \
  --from-file=ca.crt=/home/aesh/gitlab-ssl/gitlab.aesh.com.crt \
  -n gitlab-agent-minikube-agent
secret/gitlab-ca-cert created
```

В ```Secret``` помещается файл сертификата с хоста и ему дается имя ```ca.crt```.

В каталоге приложения (```~/gitlab-projects/app-7-2```) создадим файл ```agent-values.yaml```, в котором укажем параметры создания Чарта с агентом:
```yml
config:
  kasAddress: "wss://gitlab.aesh.com:8929/-/kubernetes-agent/"
  token: "токен_сгенерированный_при_создании_агента_в_GitLab"

extraEnv:
  - name: SSL_CERT_DIR
    value: "/etc/custom-ca"

extraVolumeMounts:
  - name: gitlab-ca
    mountPath: "/etc/custom-ca"
    readOnly: true

extraVolumes:
  - name: gitlab-ca
    secret:
      secretName: gitlab-ca-cert
```

```kasAddress: "wss://gitlab.aesh.com:8929/-/kubernetes-agent/"```<br>
Адрес, по которому агент обращается к ```GitLab KAS```. Должен совпадать с адресом, который записан в параметр:<br>
```gitlab_kas['external_url']```<br>
конфигурации ```GitLab```.

```token: "токен_сгенерированный_при_создании_агента_в_GitLab"```<br>
Передает токен, который хранится в секрете ```GitLab```, в конфиг агента, чтобы он при обращении мог представиться.

```
extraEnv:
  - name: SSL_CERT_DIR
    value: "/etc/custom-ca"
```
Контейнер агента будет выполнять поиск доверенных CA-сертификатов в указанном каталоге.

```
extraVolumeMounts:
  - name: gitlab-ca
    mountPath: "/etc/custom-ca"
    readOnly: true
```
Создание в контейнере агента каталога, в котором будут содержаться файлы секрета.<br>
```readOnly: true``` – агент не сможет перезаписать или удалить файлы, содержащиеся в указанном каталоге.

```
extraVolumes:
  - name: gitlab-ca
    secret:
      secretName: gitlab-ca-cert
```
Связь ```volume``` с ```Secret```. Том с именем ```gitlab-ca``` будет связан с секретом ```gitlab-ca-cert```.

Принцип взаимодействия:<br>
Агент запускается как Под в ```minikube```. Читает ```kasAddress``` и токен.<br>
Агент пытается подключиться к ```GitLab``` по адресу ```wss://gitlab.aesh.com:8929/-/kubernetes-agent/```.<br>
При установке TLS-соединения агент проверяет сертификат и фиксирует, что он самоподписанный.<br>
Агент проверяет каталог ```/etc/custom-ca``` и обнаруживает там файл сертификата ```ca.crt```.<br>
Выполняется проверка того, является ли обнаруженный сертификат подписантом сертификата сервера. При положительном результате соединение считается доверенным.<br>
Агент передает токен – ```KAS``` проверяет его в ```GitLab``` - агент регистрируется и начинает принимать команды.

Применим новые данные агента:
```bash
$ helm upgrade --install minikube-agent gitlab/gitlab-agent \
  --namespace gitlab-agent-minikube-agent \
  --set image.tag=v19.4.0 \
  -f agent-values.yaml
```

Посмтрим логи агента:
```
$ kubectl logs -n gitlab-agent-minikube-agent -l app.kubernetes.io/name=gitlab-agent \
--tail=20 | grep -E "ERROR|Successfully|leader"
{"time":"2026-10-13T12:07:07.711191639Z","level":"INFO","msg":"Attempting to acquire leader lease...",
"agent_key":"agentk:1","lock":"gitlab-agent-minikube-agent/agent-1-lock"}
{"time":"2026-10-13T12:06:54.973266476Z","level":"INFO","msg":"Attempting to acquire leader lease...",
"agent_key":"agentk:1","lock":"gitlab-agent-minikube-agent/agent-1-lock"}
{"time":"2026-10-13T12:07:18.110605262Z","level":"INFO","msg":"Successfully acquired lease",
"agent_key":"agentk:1","lock":"gitlab-agent-minikube-agent/agent-1-lock"}
{"time":"2026-10-13T12:07:18.127323566Z","level":"INFO","msg":"Event occurred","agent_key":"agentk:1",
"object":{"name":"agent-1-lock","namespace":"gitlab-agent-minikube-agent"},"fieldPath":"","kind":"Lease",
"apiVersion":"coordination.k8s.io/v1","type":"Normal","reason":"LeaderElection",
"message":"minikube-agent-gitlab-agent-v2-5f4c79b494-xbdcf became leader"}
```

Если в логах агента присутствуют ошибки, возможно, поможет перезапуск Подов агента:
```bash
kubectl rollout restart deployment/minikube-agent-gitlab-agent-v2 -n gitlab-agent-minikube-agent
```

В каталоге ```~/gitlab-runner``` создадим файл ```docker-compose.yml``` с конфигурацией нового ```runner```, который будет учитывать созданные SSL-сертификаты:
```yml
services:
  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    container_name: gitlab-runner
    restart: always
    extra_hosts:
      - "gitlab.aesh.com:host-gateway"
    volumes:
      - 'runner_config:/etc/gitlab-runner'
      - '/var/run/docker.sock:/var/run/docker.sock'
      - '~/gitlab-ssl/gitlab.aesh.com.crt:/etc/gitlab-runner/certs/gitlab.aesh.com.crt:ro'

volumes:
  runner_config:
```

Имя файла внутри контейнера (```/etc/gitlab-runner/certs/gitlab.aesh.com.crt```) должно совпадать с доменом.

Проблема аналогична проблеме подключения агента к ```GitLab``` - ```runner``` не считает сертификат ```GitLab``` доверенным.<br>
Но, если поместить файл сертификата в специальный каталог:<br>
```/etc/gitlab-runner/certs/```<br>
внутри раннера, то он автоматически будет считаться доверенным.

```:ro (Read-Only)``` – запрет на изменение/удаление файла сертификата.

Перезапустим ```runner``` - команды выполняем в том же каталоге, в котором находится файл ```docker-compose.yml``` с конфигурацией ```runner```:
```bash
docker compose down
docker compose up -d
```

В ```GitLab``` удалим старый и создадим новый ```runner```. Скопируем его токен и зарегистрируем:
```bash
$ docker exec -it gitlab-runner gitlab-runner register \
  --url https://gitlab.aesh.com:8929 \
  --registration-token токен_сгенерированный_при_создании_раннера_в_GitLab \
  --executor docker \
  --docker-image alpine:latest \
  --description "app-7-2-runner" \
  --docker-network-mode gitlab-install_default
```

В ```GitLab``` статус ```runner``` должен быть ```Online```.

Итого:<br>
```GitLab``` отдает ```HTTPS``` с правильным SAN-сертификатом.<br>
```GitLab Runner``` (через ```volume mount```) доверяет этому сертификату и может безопасно забирать задачи.<br>
```GitLab Agent``` (через ```SSL_CERT_DIR```) доверяет этому сертификату и держит туннель открытым.<br>
В результате, ```CI Job``` получает валидный ```KUBECONFIG``` и может выполнять kubectl-команды.

Настроим ```Git``` на использование нового адреса – ```https://gitlab.aesh.com:8929/root/app-7-2.git``` и поместим в ```GitLab``` все изменения:
```bash
git remote set-url origin https://gitlab.aesh.com:8929/root/app-7-2.git
git add --all
git commit -m "fix"
git -c http.sslVerify=false push
```

Перейдем в ```GitLab``` и попробуем выполнить пайплайн.<br>
Пайплайн не выполнился. Ошибка:
```
$ kubectl cluster-info
E1019 23:20:59.741659      18 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"https://gitlab.aesh.com:8929/-/kubernetes-agent/k8s-proxy/api?timeout=32s\": tls: failed to verify certificate: x509: certificate signed by unknown authority"
...
E1019 23:20:59.772291      18 memcache.go:265] "Unhandled Error" err="couldn't get current server API group list: Get \"https://gitlab.aesh.com:8929/-/kubernetes-agent/k8s-proxy/api?timeout=32s\": tls: failed to verify certificate: x509: certificate signed by unknown authority"
To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
Unable to connect to the server: tls: failed to verify certificate: x509: certificate signed by unknown authority
```

Команда ```kubectl```, которая выполняется внутри временного контейнера джобы (```google-cloud-cli```), не знает о самоподписанном сертификате. Она пытается проверить HTTPS-соединение с прокси ```KAS```, не находит доверенного центра сертификации и обрывает соединение.<br>
Это не проблема архитектуры ```KAS```. Это стандартное поведение любого Linux-контейнера при обнаружении самоподписанного сертификата.<br>
Для решения проблемы передадим CA-сертификат в джобу, сохранив значение сертификата в секретную переменную ```GitLab``` и указав ее в пайплайне.<br>
Для корректного сохранения значения сертификата, в консоли закодируем его в ```Base64```, чтобы убрать пробелы, переносы строк и т.д., которые не принимают переменные ```GitLab```.<br>
```cat ~/gitlab-ssl/gitlab.aesh.com.crt | base64 -w0```

В ```GitLab``` создадим переменную:<br>
```Settings – CI/CD – Variables – Add variable```<br>
Измененные параметры:<br>
```Key```: ```KAS_CA_CERT_B64```.<br>
```Value```: ```значение_сертификата_закодированного_в_Base64```.

Изменим файл пайплайна ```.gitlab-ci.yml```:
```yml
stages:
  - deploy

deploy:
  stage: deploy
  image: gcr.io/google.com/cloudsdktool/google-cloud-cli:latest
  script:
    # Декодируем Base64 строку обратно в валидный PEM-файл
    - echo "$KAS_CA_CERT_B64" | base64 -d > /tmp/kas-ca.crt

    # Переключаем контекст (это дает kubectl токен доступа)
    - kubectl config use-context root/app-7-2:minikube-agent

    # Проверяем ответ кластера
    - kubectl cluster-info --certificate-authority=/tmp/kas-ca.crt

    # Применяем манифест
    - kubectl apply -f k8s/deployment.yml --certificate-authority=/tmp/kas-ca.crt

    # Проверяем результат
    - kubectl get pods -l app=app-7-2 --certificate-authority=/tmp/kas-ca.crt
  environment:
    name: production
    kubernetes:
      namespace: default
```

Поместим изменения в ```GitLab```:
```bash
git add .gitlab-ci.yml
git commit -m "ci: use base64 encoded KAS_CA_CERT_B64 for reliable PEM file creation"
git -c http.sslVerify=false push
```

Перейдем в ```GitLab``` и проверим выполнение пайплайна:
```
$ echo "$KAS_CA_CERT_B64" | base64 -d > /tmp/kas-ca.crt
$ kubectl config use-context root/app-7-2:minikube-agent
Switched to context "root/app-7-2:minikube-agent".
$ kubectl cluster-info --certificate-authority=/tmp/kas-ca.crt
Kubernetes control plane is running at https://gitlab.aesh.com:8929/-/kubernetes-agent/k8s-proxy/
CoreDNS is running at https://gitlab.aesh.com:8929/-/kubernetes-agent/k8s-proxy//api/v1/namespaces/
kube-system/services/kube-dns:dns/proxy
To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
$ kubectl apply -f k8s/deployment.yml --certificate-authority=/tmp/kas-ca.crt
deployment.apps/app-7-2 unchanged
$ kubectl get pods -l app=app-7-2 --certificate-authority=/tmp/kas-ca.crt
NAME                       READY   STATUS    RESTARTS      AGE
app-7-2-5bbcdbdb98-g6qhs   1/1     Running   1 (17m ago)   23h
Cleaning up project directory and file based variables
00:01
Job succeeded
```

Пайплайн выполнился без ошибок.
