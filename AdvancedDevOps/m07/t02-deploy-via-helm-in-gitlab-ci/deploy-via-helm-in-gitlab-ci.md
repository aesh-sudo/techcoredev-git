Для решения задачи создадим каталог ```~/gitlab-projects/app-7-3```.<br>
Внури создадим helm-чарт. Структура файлов:
```
my-helm-chart
    ├── Chart.yaml
    ├── templates
    │   └── deployment.yaml
    └── values.yaml
```

Паспорт чарта – файл ```Chart.yaml```:
```yml
apiVersion: v2
name: app-7-3
description: A Helm chart for our app (app-7-3)
type: application
version: 0.1.0
appVersion: "1.0.0"
```

Настройки по умолчанию – файл ```values.yaml```:
```yml
replicaCount: 1

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: "alpine"

nameOverride: ""
fullnameOverride: ""
```

Шаблон манифеста – файл ```deployment.yaml```:
```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
  labels:
    app: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: 80
```

В ```GitLab``` создадим новый пустой проект ```app-7-3```, а в нем создадим нового агента с именем ```app-7-3-agent``` и зарегистрируем его в ```minikube```. Для этого используем ранее созданный серкет:<br>
Создадим отдельное пространство имен:
```bash
$ kubectl create namespace gitlab-agent-app-7-3
namespace/gitlab-agent-app-7-3 created
```

Скопируем секрет с сертификатом из пространства имен ```gitlab-agent-minikube-agent``` во вновь созданное пространство имен:
```bash
$ kubectl get secret gitlab-ca-cert -n gitlab-agent-minikube-agent -o yaml
 | sed 's/namespace: gitlab-agent-minikube-agent/namespace: gitlab-agent-app-7-3/'
 | kubectl apply -n gitlab-agent-app-7-3 -f -
secret/gitlab-ca-cert created
```

```-f -``` - читать манифест из стандартного ввода (```stdin```).

Установим агента:
```bash
helm upgrade --install app-7-3-agent gitlab/gitlab-agent \
  --namespace gitlab-agent-app-7-3 \
  --create-namespace \
  --set image.tag=v19.4.0 \
  --set config.token="токен_агента_из_GitLab" \
  --set config.kasAddress="wss://gitlab.aesh.com:8929/-/kubernetes-agent/" \
  --set extraEnv[0].name="SSL_CERT_DIR" \
  --set extraEnv[0].value="/etc/custom-ca" \
  --set extraVolumeMounts[0].name="gitlab-ca" \
  --set extraVolumeMounts[0].mountPath="/etc/custom-ca" \
  --set extraVolumeMounts[0].readOnly="true" \
  --set extraVolumes[0].name="gitlab-ca" \
  --set extraVolumes[0].secret.secretName="gitlab-ca-cert"
```

```app-7-3-agent``` – имя Helm-релиза (внутреннее, для ```Helm```). Может не совпадать с именем агента в ```GitLab```.<br>
```gitlab/gitlab-agent``` – Helm-чарт из репозитория ```gitlab```.

Значения остальных параметров можно найти в документации ```GitLab``` по установке агента для ```k8s```.

Посмотрим Поды агента:
```bash
$ kubectl get pods -n gitlab-agent-app-7-3
NAME                                             READY   STATUS    RESTARTS   AGE
app-7-3-agent-gitlab-agent-v2-777dc56874-7mlc7   1/1     Running   0          13m
app-7-3-agent-gitlab-agent-v2-777dc56874-fhtr6   1/1     Running   0          13m
```

Посмотрим логи агента:
```bash
$ kubectl logs -n gitlab-agent-app-7-3 -l app.kubernetes.io/name=gitlab-agent --tail=20
 | grep -E "ERROR|Successfully|leader"
{"time":"2026-10-24T08:59:49.912678259Z","level":"INFO","msg":"Attempting to acquire leader lease...",
"agent_key":"agentk:8","lock":"gitlab-agent-app-7-3/agent-8-lock"}
{"time":"2026-10-24T08:59:49.966253617Z","level":"INFO","msg":"Successfully acquired lease",
"agent_key":"agentk:8","lock":"gitlab-agent-app-7-3/agent-8-lock"}
{"time":"2026-10-24T08:59:49.988098219Z","level":"INFO","msg":"Event occurred","agent_key":"agentk:8",
"object":{"name":"agent-8-lock","namespace":"gitlab-agent-app-7-3"},"fieldPath":"","kind":"Lease",
"apiVersion":"coordination.k8s.io/v1","type":"Normal","reason":"LeaderElection",
"message":"app-7-3-agent-gitlab-agent-v2-f948984f5-sjwbr became leader"}
{"time":"2026-10-24T08:59:49.975526335Z","level":"INFO","msg":"Attempting to acquire leader lease...",
"agent_key":"agentk:8","lock":"gitlab-agent-app-7-3/agent-8-lock"}
```

Если в логах агента присутствуют ошибки, возможно, поможет перезапуск Подов агента:
```bash
kubectl rollout restart deployment/app-7-3-agent-gitlab-agent-v2 -n gitlab-agent-app-7-3
```

Вернемся в ```GitLab```, на страницу создания агента. Статус соединения созданного агента ```app-7-3-agent``` должен стать ```Connected```.

В ```GitLab``` получим токен раннера:<br>
Перейдем в меню:<br>
```Settings - CI/CD - Runners```<br>
и создадим новый токен (```Create project runner```).<br>
Параметры:<br>
```Run untagged jobs```: ```True``` – брать задания без тегов.

Нажмем ```Create runner``` и в появившейся инструкции по регистрации ```Runner``` скопируем токен вида:<br>
```glrt-XXXXXXXXXXXX```

На хосте зарегистрироуем раннер:
```bash
$ docker exec -it gitlab-runner gitlab-runner register \
  --url https://gitlab.aesh.com:8929 \
  --registration-token токен_сгенерированный_при_создании_раннера_в_GitLab \
  --executor docker \
  --docker-image alpine:latest \
  --description "app-7-3-runner" \
  --docker-network-mode gitlab-install_default
```

В ```GitLab``` создадим переменную:<br>
```Settings – CI/CD – Variables – Add variable```<br>
Измененные параметры:<br>
```Key```: ```KAS_CA_CERT_B64```.<br>
```Value```: значение_сертификата_закодированного_в_Base64.

Получить значение сертификата, закодированного в ```Base64``` можно так:<br>
```base64 -w 0 ~/gitlab-ssl/gitlab.aesh.com.crt```

Пайплайн – файл ```.gitlab-ci.yml```:
```yml
stages:
  - deploy

deploy:
  stage: deploy
  image: dtzar/helm-kubectl:latest
  script:
    # Декодируем Base64 строку обратно в валидный PEM-файл
    - echo "$KAS_CA_CERT_B64" | base64 -d > /tmp/kas-ca.crt

    # Переключаем контекст kubectl на нового агента
    - kubectl config use-context root/app-7-3:app-7-3-agent

    # Деплой через Helm
    # --install: установит релиз, если его еще нет в кластере
    # --upgrade: обновит релиз, если он уже существует
    # --kube-context: явно указываем Helm, какой контекст использовать
    - helm upgrade --install my-nginx-release ./my-helm-chart --kube-context root/app-7-3:app-7-3-agent --kube-ca-file=/tmp/kas-ca.crt

    # Проверяем, что поды успешно создались
    - kubectl get pods --certificate-authority=/tmp/kas-ca.crt
```

Создадим репозиторий и перенесем файлы проекта ```app-7-3``` в ```GitLab```:
```bash
git init
git remote add origin https://gitlab.aesh.com:8929/root/app-7-3.git
git add .
git commit -m "add app-7-3"
git -c http.sslVerify=false push
```

Перейдем в ```GitLab``` и проверим выполнение пайплайна:
```
$ echo "$KAS_CA_CERT_B64" | base64 -d > /tmp/kas-ca.crt
$ kubectl config use-context root/app-7-3:app-7-3-agent
Switched to context "root/app-7-3:app-7-3-agent".
$ helm upgrade --install my-nginx-release ./my-helm-chart --kube-context root/app-7-3:app-7-3-agent --kube-ca-file=/tmp/kas-ca.crt
Release "my-nginx-release" has been upgraded. Happy Helming!
NAME: my-nginx-release
LAST DEPLOYED: Sun Oct 25 11:44:38 2026
NAMESPACE: default
STATUS: deployed
REVISION: 6
DESCRIPTION: Upgrade complete
TEST SUITE: None
$ kubectl get pods --certificate-authority=/tmp/kas-ca.crt
NAME                                           READY   STATUS    RESTARTS        AGE
app-7-2-84c599b597-mkmfv                       1/1     Running   12              15d
db-95d7985b-zw6j5                              1/1     Running   43              39d
my-nginx-release-deployment-86df65746f-6mf56   1/1     Running   2 (4m17s ago)   47h
Cleaning up project directory and file based variables
00:01
Job succeeded
```

Пайплайн выполнился без ошибок.
