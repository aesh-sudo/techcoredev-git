Для решения задачи у нас есть:
* Файл ```minikube-config``` в ```Credentials```.
* Агент в контейнере с ```kubectl```.

Создадим приложение ```my-app```:<br>
Файл приложения ```app.py```:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import os, socket

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        hostname = socket.gethostname()
        self.wfile.write(f"my-app running on {hostname}\n".encode())

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8081'))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Server running on port {port}")
    server.serve_forever()
```

Файл ```dockerfile```:
```
FROM python:3.11-alpine
WORKDIR /app
COPY app.py .
EXPOSE 8081
CMD ["python", "app.py"]
```

Соберем образ приложения и загрузим его в ```minikube```:
```bash
docker build -f dockerfile -t my-app:latest .
minikube image load my-app:latest
```

Проверим наличие образа приложения ```my-app``` в ```minikube```:
```bash
$ minikube ssh -- sudo crictl images | grep my-app
my-app                                               latest              8265b6e683528       54.6MB
```

Создадим файл ```deployment.yml```:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: my-app:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8081
```

```imagePullPolicy: IfNotPresent``` – в первую очередь наличие образа проверяется на Ноде.

Создадим файл агента – ```Jenkinsfile```:
```yaml
pipeline {
    agent {
        docker {
            image 'lachlanevenson/k8s-kubectl:v1.25.0'
            args '--entrypoint= --network=minikube'
        }
    }
    stages {
        stage('Verify kubectl') {
            steps {
                sh 'kubectl version --client'
            }
        }
        stage('Deploy to K8s') {
            steps {
                withCredentials([file(credentialsId: 'minikube-config', variable: 'KUBECONFIG')]) {
                    sh 'kubectl apply -f k8s/deployment.yml'
                    sh 'kubectl get pods'
                }
            }
        }
    }
}
```

```--network=minikube``` – контейнер-агент должен быть в одной сети с ```minikube```.

```withCredentials``` – ```Jenkins``` пробросит файл ```minikube-config``` в агент и установит переменную окружения ```KUBECONFIG```. После выхода из блока файл удалится.

Структура проекта:
```
~/k8s-ci-cd/myapp/
├── app.py
├── dockerfile
├── Jenkinsfile          # пайплайн
└── k8s
    └── deployment.yml   # манифест, который деплоим
```

В файле ```minikube-config``` сертификаты указаны путями, то есть внутри контейнера файлов сертификатов нет.<br>
Сформируем в отдельном файле полный конфиг текущего кластера, без сокращений и ссылок:
```bash
kubectl config view --minify --raw --flatten >
 ~/techcoredev-git/AdvancedDevOps/m06/t03-add-k8s-deploy-stage-and-evolve-to-helm/kubeconfig-selfcontained
```

```view``` – показать конфиг ```kubectl```.<br>
```--minify``` – оставить только то, что относится к текущему контексту (что реально используется).<br>
```--raw``` – показать данные как есть, без маскировки секретов и форматирования.<br>
```--flatten``` – вставить содержимое всех ссылок в конфиг.

Обновим ```Credential``` ```minikube-config``` в ```Jenkins```:<br>
```Manage Jenkins - Credentials - System - Global```<br>
Выбираем ```minikube-config``` и нажимаем ```Update credential```.<br>
Ставим галочку ```Replace``` (заменить), выбираем файл конфига ```kubeconfig-selfcontained``` и сохраняем ```Credential```.

Опубликуем проект в ```GitHub```:
```bash
cd ~/k8s-ci-cd/myapp
git init
git add .
git commit -m "Jenkinsfile + k8s deployment"
```

В ```GitHub``` создадим репозиторий ```myapp```. Перейдем в консоль и поместим изменения в ```GitHub```:
```bash
remote add origin git@github.com:aesh-sudo/myapp.git
git branch -M main
git push -u origin main
```

Так как данные будем брать из репозитория ```GitHub```, то в ```Jenkins``` создадим ```Credentials```, в котором сохраним ```PAT``` от ```GitHub```.<br>
Выберем меню:<br>
```Manage Jenkins – Credentials - Add Credentials```<br>
Выберем тип создаваемых данных:<br>
```Username with password```

```Scope``` (масштаб использования учетных данных):<br>
```Global (Jenkins, nodes, items, all child items, etc)```

```Username``` – так как мы хотим использовать ```Jenkinsfile``` из репозитория в ```GitHub```, то параметр заполним именем пользователя ```GitHub```.

```Password``` – ```PAT``` (```Personal Access Token```) учетной записи в ```GitHub```, так как:
* Токен можно отозвать в любой момент.
* Токен ограничен по правам.
* Токен уникален только для ```GitHub```.

Далее в ```Jenkins``` создадим конфигурацию с именем ```myapp-deploy``` и типом ```Pipeline```.<br>
Настройки:<br>
Секция ```Pipeline```:<br>
```Definition``` – выбираем значение ```Pipeline script from SCM```.<br>
```SCM``` - выбираем пункт ```Git``` и заполняем поле:<br>
```Repository URL``` (адрес репозитория):<br>
```https://github.com/aesh-sudo/myapp.git```<br>
```Credentials``` – выберем ```Credentials```, созданный ранее.

```Branches to build``` – ветка/ветки репозитория для сборки ```Jenkins```:<br>
```*/main```

```Script Path``` – ```Jenkinsfile``` (значение по умолчанию).

Сохраним и запустим сборку, нажав ```Build Now```.

При запуске ```Jenkins```:<br>
Клонирует репозиторий в ```workspace``` - Находит ```Jenkinsfile``` (агента) в корне - Запускает пайплайн.

Проверим созданные объекты на хосте:
```bash
$ kubectl get pods
NAME                            READY   STATUS    RESTARTS         AGE
myapp-5d4ff8dff6-lsxgz          1/1     Running   0                105s

$ kubectl get deploy myapp
NAME    READY   UP-TO-DATE   AVAILABLE   AGE
myapp   1/1     1            1           3m14s
```

Проверка результата:
```bash
$ kubectl port-forward deploy/myapp 8081:8081 &
$ curl http://localhost:8081
Handling connection for 8081
my-app running on myapp-5d4ff8dff6-lsxgz
```

########## 6

Обновим файл манифеста – ```deployment.yml```:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
#          image: my-app:latest
          image: my-app:IMAGE_TAG
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8081
```

```IMAGE_TAG``` – текст, который ```sed``` заменит на номер релиза.

Обновим файл агента – ```Jenkinsfile```:
```
pipeline {
    agent {
        docker {
            image 'lachlanevenson/k8s-kubectl:v1.25.0'
            args '--entrypoint= --network=minikube'
        }
    }
    stages {
        stage('Verify kubectl') {
            steps {
                sh 'kubectl version --client'
            }
        }
        stage('Prepare manifests') {
            steps {
                sh "sed -i 's/IMAGE_TAG/${BUILD_NUMBER}/g' k8s/deployment.yml"
                sh 'cat k8s/deployment.yml | grep image:'
            }
        }
        stage('Deploy to K8s') {
            steps {
                withCredentials([file(credentialsId: 'minikube-config', variable: 'KUBECONFIG')]) {
                    sh 'kubectl apply -f k8s/deployment.yml'
                    sh 'kubectl get pods'
                }
            }
        }
    }
}
```

```sed``` – команда для потокового редактирования текста.<br>
```-i``` - редактировать исходный файл, перезаписывая его.<br>
```'s/OLD/NEW/g'``` - заменить ```OLD``` на ```NEW``` глобально.<br>
```${BUILD_NUMBER}``` - переменная ```Groovy``` (номер сборки ```Jenkins```), подставляется до выполнения ```sed```.

Подготовим образы для нескольких релизов:<br>
Удалим старый ```Deployment```:
```bash
kubectl delete deploy myapp
```

Пересоберем образ приложения:
```bash
docker build --no-cache -f dockerfile -t my-app:latest .
```

Создадим теги для двух релизов приложения:
```bash
docker tag my-app:latest my-app:1
docker tag my-app:latest my-app:2
```

Проверим результат:
```bash
$ docker images
                                                                                          i Info →   U  In Use
IMAGE           ID             DISK USAGE   CONTENT SIZE   EXTRA
my-app:1        21a437be4535       83.9MB        20.4MB
my-app:2        21a437be4535       83.9MB        20.4MB
my-app:latest   21a437be4535       83.9MB        20.4MB
```

Удалим образ приложения, который был загружен в ```minikube``` ранее:
```bash
minikube image rm my-app:latest
```

Загрузим новые релизы образа в ```minikube``` и проверим результат:
```bash
minikube image load my-app:latest
minikube image load my-app:1
minikube image load my-app:2

$ minikube ssh -- sudo crictl images | grep my-app
IMAGE                                                TAG                 IMAGE ID            SIZE
my-app                                               1                   4913f9036d3cb       54.6MB
my-app                                               2                   4913f9036d3cb       54.6MB
my-app                                               latest              4913f9036d3cb       54.6MB
```

Поместим файлы приложения в ```GitHub```:
```bash
git add .
git commit -m "Dynamic image tags with sed"
git push
```

В ```Jenkins``` для чистоты эксперимента лучше удалить и заново создать конфигурацию ```myapp-deploy```, так как номер сборки должен совпадать с номером релиза образа.

Запустим сборку конфигурации ```myapp-deploy```, нажав ```Build Now```. Процесс выполнения можно посмотреть, нажав на номер сборки и перейдя в пункт меню ```Console Output```.<br>
Результат сборки проверим в консоли:
```bash
$ kubectl get pods
NAME                            READY   STATUS    RESTARTS       AGE
myapp-5f4fdb5668-5kl8k          1/1     Running   0              106s

$ kubectl get deploy myapp -o yaml | grep image:
      - image: my-app:1
```

Запустим сборку второй раз и проверим результат:
```bash
$ kubectl get pods
NAME                            READY   STATUS    RESTARTS       AGE
myapp-c5565d669-wv5pq           1/1     Running   0              43s

$ kubectl get deploy myapp -o yaml | grep image:
      - image: my-app:2
```

Видим, что Под пересоздался из нового релиза образа.

########## 7

В каталоге приложения (```~/k8s-ci-cd/myapp```) создадим Чарт:<br>
Структура файлов Чарта:
```
.
├── Chart.yaml
├── templates
│   └── deployment.yaml
└── values.yaml
```

Зададим метаданные Чарта - файл ```Chart.yaml```:
```yaml
apiVersion: v2
name: my-app-chart
description: Helm chart for my-app
type: application
version: 0.1.0
appVersion: "1.0"
```

Зададим настройки и их значения - файл ```values.yaml```:
```yaml
replicaCount: 1

image:
  repository: my-app
  tag: "latest"              # значение по умолчанию. В агенте переопределим через --set
  pullPolicy: IfNotPresent

containerPort: 8081
```

В каталоге шаблонов ```templates``` создадим файл с описанием развертывания приложения – ```deployment.yaml```:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
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
        - name: {{ .Release.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.containerPort }}
```

```{{ .Release.Name }}``` – имя релиза из команды установки Чарта (в Агенте).<br>
```{{ .Values.image.tag }}``` - значение из ```values.yaml```.

Проверим Чарт локально – из каталога ```~/k8s-ci-cd/myapp```:
```bash
$ helm lint helm-charts/my-app-chart
==> Linting helm-charts/my-app-chart
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed

$ helm template my-app helm-charts/my-app-chart --set image.tag=99 | grep -E "name:|image:"
  name: my-app
        - name: my-app
          image: "my-app:99"
```

```helm template``` – генерирует k8s-манифест из Чарта, подставляя значения в шаблоны, но не применяет их в кластере.

Обновим файл агента – ```Jenkinsfile```:
```
pipeline {
    agent {
        docker {
            image 'lachlanevenson/k8s-kubectl:v1.25.0'
            args '--entrypoint= --network=minikube'
        }
    }
    stages {
        stage('Deploy to K8s') {
            steps {
                withCredentials([file(credentialsId: 'minikube-config', variable: 'KUBECONFIG')]) {
                    sh '''
                        curl -fsSL -o helm.tar.gz https://get.helm.sh/helm-v3.14.3-linux-amd64.tar.gz
                        tar -xzf helm.tar.gz
                        export PATH=$PWD/linux-amd64:$PATH
                        helm upgrade --install my-app ./helm-charts/my-app-chart
                           --set image.tag=${BUILD_NUMBER}
                    '''
                    sh 'kubectl get pods'
                }
            }
        }
    }
}
```

В образе агента ```lachlanevenson/k8s-kubectl``` нет ```helm```, поэтому выполняется его установка. Вся команда выполняется в одном блоке ```sh '''...'''```, чтобы не потерять значение переменной ```PATH```, так как для каждого ```sh``` запускается новая оболочка.

```helm upgrade –install``` – команда выполняет ```upgrade```, если релиз уже установлен, и ```install```, если релиз еще не установлен.<br>
Синтаксис:
```bash
helm upgrade --install <имя-релиза> <путь-к-чарту> [флаги]
```

Для проверки решения удалим ```deployment```, который был сделан в прошлой задаче:
```bash
$ kubectl delete deploy myapp
deployment.apps "myapp" deleted from default namespace
```

В ```Jenkins``` для чистоты эксперимента лучше удалить и заново создать конфигурацию ```myapp-deploy```, так как номер сборки должен совпадать с номером релиза образа.

Поместим файлы приложения в ```GitHub``` - перед этим перейдем в каталог ```~/k8s-ci-cd/myapp```:
```bash
git add .
git commit -m "Deploy via Helm instead of sed"
git push
```

Запустим сборку конфигурации ```myapp-deploy```, нажав ```Build Now```. Процесс выполнения можно посмотреть, нажав на номер сборки и перейдя в пункт меню ```Console Output```.<br>
Результат сборки проверим в консоли:
```bash
$ kubectl get pods
NAME                            READY   STATUS    RESTARTS       AGE
myapp-5f4fdb5668-5kl8k          1/1     Running   0              106s

$ helm list
NAME    NAMESPACE       REVISION        UPDATED                                 STATUS
   CHART                   APP VERSION
my-app  default         1               2026-09-23 16:16:42.139895206 +0000 UTC deployed
   my-app-chart-0.1.0      1.0

$ helm history my-app
REVISION        UPDATED                         STATUS          CHART                   APP VERSION
   DESCRIPTION
1               Wed Sep 23 16:16:42 2026        deployed        my-app-chart-0.1.0      1.0
   Install complete

$ kubectl get deploy my-app -o yaml | grep image:
      - image: my-app:1
```

Запустим сборку второй раз и проверим результат:
```bash
$ kubectl get pods
NAME                            READY   STATUS    RESTARTS       AGE
my-app-f6dbf6987-rtrsd          1/1     Running   0              118s

$ helm list
NAME    NAMESPACE       REVISION        UPDATED                                 STATUS
   CHART                   APP VERSION
my-app  default         2               2026-09-23 16:23:48.353507308 +0000 UTC deployed
   my-app-chart-0.1.0      1.0

$ helm history my-app
REVISION        UPDATED                         STATUS          CHART                   APP VERSION
   DESCRIPTION
1               Wed Sep 23 16:16:42 2026        superseded      my-app-chart-0.1.0      1.0
   Install complete
2               Wed Sep 23 16:23:48 2026        deployed        my-app-chart-0.1.0      1.0
   Upgrade complete

$ kubectl get deploy my-app -o yaml | grep image:
      - image: my-app:2
```
