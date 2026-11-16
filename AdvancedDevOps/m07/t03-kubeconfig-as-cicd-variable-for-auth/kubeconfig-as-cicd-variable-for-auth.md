Структура проекта:
```bash
$ tree -a -I ".git"
.
├── .gitlab-ci.yml
├── k8s
│   └── deployment.yml
└── kubeconfig-for-ci.yml
```

Файл конфигурации для развертывания ```GitLab```:
```bash
$ cat docker-compose-gitlab.yml
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

        # HTTPS
        nginx['ssl_certificate'] = "/etc/gitlab/ssl/gitlab.aesh.com.crt"
        nginx['ssl_certificate_key'] = "/etc/gitlab/ssl/gitlab.aesh.com.key"
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

Файл конфигурации для развертывания раннера:
```bash
$ cat docker-compose-runner.yml
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
      - '/home/aesh/gitlab-ssl/gitlab.aesh.com.crt:/etc/gitlab-runner/certs/gitlab.aesh.com.crt:ro'
    networks:
      - gitlab-install_default

volumes:
  runner_config:

# Объявляем сеть как внешнюю, чтобы Docker Compose не пытался создать ее заново,
# а использовал уже существующую в системе
networks:
  gitlab-install_default:
    external: true
```

В ```GitLab``` получим токен раннера:<br>
Перейдем в меню:<br>
```Settings - CI/CD - Runners```<br>
и создадим новый токен (```Create project runner```).<br>
Параметры:<br>
```Run untagged jobs```: ```True``` – брать задания без тегов.

Нажмем ```Create runner``` и в появившейся инструкции по регистрации скопируем токен вида:<br>
```glrt-XXXXXXXXXXXX```

По умолчанию раннер создает для каждой джобы изолированный контейнер в стандартной сети:<br>
```Docker (bridge, 172.17.x.x)```<br>
Из этой сети нет маршрута к сети:<br>
```minikube (192.168.49.x)```<br>
Что приводит к ошибкам ```i/o timeout``` или ```connection refused```.

На хосте зарегистрируем раннер. Когда ```executor – docker```, раннер для каждой джобы создает временный контейнер (или несколько) и запускает в нем шаги из ```.gitlab-ci.yml```. Параметр ```network-mode``` указывает ```Docker```, в какой сетевой среде запускать эти контейнеры:
```bash
$ docker exec -it gitlab-runner gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.aesh.com:8929" \
  --registration-token "токен_сгенерированный_при_создании_раннера_в_GitLab" \
  --executor "docker" \
  --docker-image "alpine/k8s:1.35.9" \
  --description "app-7-4-runner" \
  --docker-network-mode "gitlab-install_default" \
  --docker-extra-hosts "gitlab.aesh.com:host-gateway" \
  --docker-volumes "/cache"
```

```docker-extra-hosts``` – добавляет в файл ```/etc/hosts``` временного контейнера раннера запись вида:<br>
```IP-адрес имя_хоста```

```host-gateway``` – обозначает шлюз хоста, откуда будут копироваться данные (во временный контейнер).

В итоге получается запись, которая указывает ip-адрес контейнера с ```GitLab```, соответствующий адресу ```gitlab.aesh.com```.

Пайплайн – файл ```.gitlab-ci.yml```:
```yml
stages:
  - deploy

deploy:
  stage: deploy
  image: alpine/k8s:1.35.9
  script:
    # Декодируем Base64-строку обратно в kubeconfig-файл
    - echo "$KUBE_CONFIG" | base64 -d > /tmp/kubeconfig.yml

    # Проверяем, что файл создался и валидный
    - head -n 10 /tmp/kubeconfig.yml

    # Используем kubeconfig для получения информации о кластере
    - kubectl --kubeconfig /tmp/kubeconfig.yml cluster-info

    # Получаем список Подов в namespace default
    - kubectl --kubeconfig /tmp/kubeconfig.yml get pods -n default

    # Применяем манифест
    - kubectl --kubeconfig /tmp/kubeconfig.yml apply -f k8s/deployment.yml
  environment:
    name: production
    kubernetes:
      namespace: default
```

Запустим ```minikube``` так:
```bash
minikube start --apiserver-names=k8s.local --listen-address=0.0.0.0 --apiserver-ips=192.168.1.92
```

```apiserver-ips``` – добавляет указанный ip-адрес в список разрешенных имен (```SAN - Subject Alternative Names```) TLS-сертификата, который ```minikube``` генерирует при старте.<br>
Когда клиент пытается подключиться по адресу:<br>
```https://192.168.1.92:32771```<br>
```minikube``` проверяет сертификат. Если ip-адрес хоста (```192.168.1.92```) не прописан в сертификате как разрешенный, соединение будет разорвано с ошибкой:<br>
```x509: certificate is valid for 192.168.49.2, not 192.168.1.92.```

```192.168.1.92``` – ip-адрес хоста.

```apiserver-names``` – добавляет указанное доменное имя в список разрешенных имен (```SAN```) TLS-сертификата.<br>
Сейчас в сертификате мы используем ip-адрес, но наличие доменного имени позволяет в будущем легко переключиться на подключение по имени (например, если будет настроен локальный ```DNS``` или Nginx-прокси), без необходимости пересоздавать кластер и сертификаты.

Посмотрим файл конфигурации ```minikube``` (```kubeconfig```):
```bash
$ cat ~/.kube/config
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /home/aesh/.minikube/ca.crt
    extensions:
    - extension:
        last-update: Sun, 15 Nov 2026 20:09:01 UTC
        provider: minikube.sigs.k8s.io
        version: v1.39.0
      name: cluster_info
    server: https://192.168.49.2:8443
  name: minikube
contexts:
- context:
    cluster: minikube
    extensions:
    - extension:
        last-update: Sun, 15 Nov 2026 20:09:01 UTC
        provider: minikube.sigs.k8s.io
        version: v1.39.0
      name: context_info
    namespace: default
    user: minikube
  name: minikube
current-context: minikube
kind: Config
users:
- name: minikube
  user:
    client-certificate: /home/aesh/.minikube/profiles/minikube/client.crt
    client-key: /home/aesh/.minikube/profiles/minikube/client.key
```

Секции:<br>
```clusters``` – информация о кластерах (адрес API-сервера, сертификаты).<br>
```contexts``` – контексты (связь между пользователем и кластером).<br>
```users``` – пользователи и их ```credentials``` (токены, сертификаты).<br>
```current-context``` – контекст, используемый по умолчанию.

Так как пайплайн будет выполняться внутри временного Docker-контейнера, то файлы сертификатов, которые находятся на хосте, в нем будут недоступны. Поэтому вместо путей к сертификатам, поместим их значения в конфиг:<br>
```kubectl config view --minify --flatten > kubeconfig-for-ci.yml```

Узнаем внешний порт контейнера ```minikube```:
```bash
$ docker port minikube 8443/tcp
0.0.0.0:32771
```

Отредактируем файл: адрес сервера должен совпадать с адресом хоста, а порт сервера – с внешним портом ```minikube```:<br>
```server: https://192.168.1.92:32771```

Протестируем получившийся конфиг локально:<br>
```$ kubectl --kubeconfig kubeconfig-for-ci.yml get pods```<br>
Если команда вернула список Подов, значит конфиг корректный.

Закодируем конфиг в ```Base64```:
```bash
cat kubeconfig-for-ci.yml | base64 -w 0
```

Полученное значение поместим в переменную ```GitLab```:<br>
```Settings – CI/CD – Variables – Add variable```<br>
Измененные параметры:<br>
```Key```: ```KUBE_CONFIG```.
```Value```: ```значение_сертификата_закодированного_в_Base64```.

Принцип взаимодействия:<br>
Временный контейнер джобы, находящийся в сети ```gitlab-install_default```, читает файл конфигурации ```kubeconfig-for-ci.yml```, в котором указан адрес, по которому клиент (например, ```kubectl```) может подключиться к API-серверу кластера:<br>
```server: https://192.168.1.92:32771```<br>
У контейнера ```minikube``` выполнен проброс портов:<br>
```0.0.0.0:32771->8443/tcp```<br>
и API-сервер внутри ```minikube``` слушает все интерфейсы:<br>
```--listen-address=0.0.0.0```

Файл ```deployment.yml```:
```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-direct
  labels:
    app: nginx-direct
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-direct
  template:
    metadata:
      labels:
        app: nginx-direct
    spec:
      containers:
        - name: nginx
          image: nginx:alpine
          ports:
            - containerPort: 80
```

Создадим репозиторий и перенесем файлы проекта ```app-7-4``` в ```GitLab```:
```bash
git init
git remote add origin https://gitlab.aesh.com:8929/root/app-7-4.git
git add .
git commit -m "add app-7-4"
git -c http.sslVerify=false push --set-upstream origin master
```
При повторном переносе изменений можно использовать:
```bash
git -c http.sslVerify=false push
```
