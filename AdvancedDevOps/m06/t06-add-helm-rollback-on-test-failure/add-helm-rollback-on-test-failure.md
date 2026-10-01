В ```Jenkinsfile``` можно использовать стандартные конструкции обработки ошибок:
```
script {
    try {
        // код, который может вызвать ошибку
        sh 'helm upgrade --install ...'
        sh 'curl http://app:8081/health'
    } catch (Exception e) {
        // обработка ошибки
        sh 'helm rollback my-app'
        throw e  // пробрасываем ошибку дальше (сборка помечается как failed)
    }
}
```

```try...catch``` – это Groovy-код, а не declarative-шаг, поэтому его необходимо обернуть в блок ```script```.<br>
```throw e``` – если не пробросить ошибку дальше, то сборка будет помечена как успешная.

Создадим приложения для тестирования в каталоге:<br>
```~/k8s-ci-cd/app-6-10```

Файл рабочего приложения - ```app-6-10-worker.py```:
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import os, socket

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        hostname = socket.gethostname()
        self.wfile.write(f"app-6-10 worker running on {hostname}\n".encode())

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8081'))
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Worker running on port {port}")
    server.serve_forever()
```

Файл сломанного приложения - ```app-6-10-broken.py```:
```python
import sys
print("app-6-10 broken: application failed to start!")
sys.exit(1)
```

```dockerfile-worker```:
```python
FROM python:3.11-alpine
WORKDIR /app
COPY app-6-10-worker.py .
EXPOSE 8081
CMD ["python", "app-6-10-worker.py"]
```

```dockerfile-broken```:
```python
FROM python:3.11-alpine
WORKDIR /app
COPY app-6-10-broken.py .
EXPOSE 8081
CMD ["python", "app-6-10-broken.py"]
```

Соберем образы приложений и загрузим в ```minikube```:
```bash
docker build -f dockerfile-worker -t app-6-10:worker .
docker build -f dockerfile-broken -t app-6-10:broken .

minikube image load app-6-10:worker
minikube image load app-6-10:broken
```

Проверим загруженные образы в ```minikube```:
```bash
$ minikube ssh -- sudo crictl images | grep app-6-10
IMAGE      TAG      IMAGE ID        SIZE
app-6-10   broken   657671432b3d9   54.6MB
app-6-10   worker   9251a2ede4b0a   54.6MB
```

Создадим Чарт ```app-6-10-chart``` в каталоге ```helm-charts```. Он будет аналогичен Чарту из задачи 7, поэтому скопируем его оттуда, а в файлах изменим названия.

Создадим ```Jenkinsfile```:
```
pipeline {
    agent {
        kubernetes {
            inheritFrom 'jenkins-agent'
            defaultContainer 'kubectl'
            yaml '''
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins
  containers:
  - name: kubectl
    image: lachlanevenson/k8s-kubectl:v1.25.0
    command:
    - sleep
    args:
    - infinity
'''
        }
    }
    parameters {
        string(name: 'IMAGE_TAG', defaultValue: 'worker', description: 'Тег образа для деплоя')
    }
    stages {
        stage('Deploy and Test') {
            steps {
                script {
                    try {
                        sh '''
                            curl -fsSL -o helm.tar.gz https://get.helm.sh/helm-v3.14.3-linux-amd64.tar.gz
                            tar -xzf helm.tar.gz
                            export PATH=$PWD/linux-amd64:$PATH
                            helm upgrade --install app-6-10 ./helm-charts/app-6-10-chart \
                              --set image.repository=app-6-10 \
                              --set image.tag=${IMAGE_TAG}
                        '''
                        
                        // Smoke Test
                        sh '''
                            kubectl rollout status deployment/app-6-10 --timeout=60s
                            kubectl port-forward deploy/app-6-10 8081:8081 &
                            sleep 5
                            curl -f http://localhost:8081 || exit 1
                            kill %1
                        '''
                        
                        echo 'Deploy and Smoke Test passed'
                    } catch (Exception e) {
                        echo "Deploy or Smoke Test failed: ${e.message}"
                        echo 'Attempting rollback...'
                        try {
                            sh '''
                                curl -fsSL -o helm.tar.gz https://get.helm.sh/helm-v3.14.3-linux-amd64.tar.gz
                                tar -xzf helm.tar.gz
                                export PATH=$PWD/linux-amd64:$PATH
                                helm rollback app-6-10
                            '''
                        } catch (Exception rollbackError) {
                            echo "Rollback не выполнен (нечего откатывать): ${rollbackError.message}"
                        }
                        throw e
                    }
                }
            }
        }
    }
}
```

```pipeline{...parameters{...}...}``` – блок, описывающий список параметров, которые пользователь должен указать при запуске сборки.<br>
Синтаксис:
```
parameters {
    string(name: 'PARAM_NAME', defaultValue: 'value', description: 'Описание параметра')
    // Другие типы параметров...
}
```

Типы параметров:<br>
```string``` - строковый параметр.<br>
```text``` - многострочный текстовый параметр.<br>
```booleanParam``` - булев параметр (истина/ложь).<br>
```choice``` - параметр с выпадающим списком значений.<br>
```password``` - параметр для ввода пароля (не отображается в интерфейсе, но учитывается при запуске).

```params``` – объект, через который заданные параметры доступны в коде.

```${IMAGE_TAG}``` – переменная окружения, которую ```Jenkins``` автоматически экспортирует из параметров пайплайна.<br>
```--set image.tag=${IMAGE_TAG}``` – задание тега образа. ```shell``` раскроет переменную окружения в значение параметра.

В ```Smoke Test``` выполняется создание безопасного туннеля между Клиентом (```k8s```) и Подом Деплоймента. Для выполнения этой команды в правила прав для основной группы необходимо добавить туннель (```pods/portforward```). Добавляем в файле ```jenkins-sa.yaml```, который будет полной копией аналогичного файла из прошлой задачи, за исключением добавленного туннеля:
```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: jenkins
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods", "pods/exec", "pods/log", "pods/portforward", "secrets", "configmaps"]
  verbs: ["*"]
```

Применим ```ServiceAccount```, ```Role``` и ```RoleBinding``` (описаны в одном файле):
```bash
$ kubectl apply -f jenkins-sa.yaml
```

Проверим право:
```bash
$ kubectl auth can-i create pods/portforward --as=system:serviceaccount:default:jenkins
yes
```

```kubectl auth can-i create pods/portforward``` - команда проверит, сможет ли текущий пользователь создать ```kubectl port-forward``` к Подам.<br>
```--as=...``` – флаг, указывающий аккаунт, от имени которого надо проверить выполение команды.<br>
```system:serviceaccount:<namespace>:<name>``` - полное имя аккаунта.

Внутренний ```try...catch``` в ```catch```:<br>
Если первый деплой упал до того, как ```Helm``` создал релиз, то ```helm rollback``` упадет с ошибкой, так как система не сможет найти успешный релиз для отката. Внутренний ```try...catch``` в ```catch``` перехватит эту ошибку, выведет предупреждение, но основную ошибку все равно пробросит через ```throw e``` - сборка будет помечена как ошибочная.

Опубликуем проект в ```GitHub```:
```bash
cd ~/k8s-ci-cd/app-6-10
git init
git add .
git commit -m "add app-6-10"
```

В ```GitHub``` создадим репозиторий ```app-6-10```. Перейдем в консоль и поместим изменения в ```GitHub```:
```bash
remote add origin git@github.com:aesh-sudo/ app-6-10.git
git branch -M main
git push -u origin main
```

Тестирование:<br>
Очистим предыдущий релиз (если он был):
```bash
$ helm delete app-6-10 2>/dev/null || true
release "app-6-10" uninstalled
kubectl delete deploy app-6-10 2>/dev/null || true
```

```kubectl delete deploy``` – контроль удаления. На случай, если ```Deployment``` был создан/изменен без участия ```Helm```.

В ```Jenkins``` создадим новую конфигурацию ```app-6-10``` типа ```Pipeline```:<br>
Настройки:<br>
Секция ```This project is parameterized```:<br>
```Name```: ```IMAGE_TAG```.<br>
```Default Value```: ```worker```.<br>
```Description```: Тег образа для деплоя.

В ```Declarative Pipeline``` блок ```parameters { }``` регистрируется в ```Jenkins``` только после первого прогона пайплайна. Чтобы первый пайплайн завершился удачно, мы задали параметры в настройках конфигурации.
Кнопка ```Build Now``` после этого будет переименована в ```Build with Parameters```.

Секция ```Pipeline```:<br>
```Definition``` – выбираем значение ```Pipeline script from SCM```.<br>
```SCM``` - выбираем пункт ```Git``` и заполняем поле:<br>
```Repository URL``` (адрес репозитория):<br>
```https://github.com/aesh-sudo/app-6-10.git```<br>
```Credentials```:<br>
```aesh-sudo/****** (GitHub Personal Access Token)```

```Branches to build``` – ветка/ветки репозитория для сборки ```Jenkins```:<br>
```*/main```

```Script Path```: ```Jenkinsfile``` (по умолчанию, так как ```Jenkinsfile``` находится в корне каталога приложения).

Сохраним и запустим сборку, нажав ```Build with Parameters```. Будет показан параметр ```IMAGE_TAG```, оставим значение по умолчанию.

После завершения деплоя проверим историю ```Helm```:
```bash
$ helm history app-6-10
REVISION        UPDATED                         STATUS          CHART                   APP VERSION
   DESCRIPTION
1               Wed Sep 30 23:52:00 2026        deployed        app-6-10-chart-0.1.0    1.0
   Install complete
```

Теперь запустим сборку сломанного приложения. Деплой завершится с ошибкой. Проверим историю ```Helm```:
```bash
$ helm history app-6-10
REVISION        UPDATED                         STATUS          CHART                   APP VERSION
   DESCRIPTION
1               Wed Sep 30 23:52:00 2026        superseded      app-6-10-chart-0.1.0    1.0
   Install complete
2               Wed Sep 30 23:57:16 2026        superseded      app-6-10-chart-0.1.0    1.0
   Upgrade complete
3               Wed Sep 30 23:58:36 2026        deployed        app-6-10-chart-0.1.0    1.0
   Rollback to 1
```

Видим, что Под вернулся к образу ```app-6-10:worker``` и продолжает работу:
```bash
$ kubectl get pods
NAME                        READY   STATUS    RESTARTS        AGE
app-6-10-564b76fdb5-x4625   1/1     Running   0               10m
```

Снова выполним сборку рабочего (```worker```) приложения и проверим результат:
```bash
$ helm history app-6-10
REVISION        UPDATED                         STATUS          CHART                   APP VERSION
   DESCRIPTION
1               Wed Sep 30 23:52:00 2026        superseded      app-6-10-chart-0.1.0    1.0
   Install complete
2               Wed Sep 30 23:57:16 2026        superseded      app-6-10-chart-0.1.0    1.0
   Upgrade complete
3               Wed Sep 30 23:58:36 2026        superseded      app-6-10-chart-0.1.0    1.0
   Rollback to 1
4               Thu Oct  1 00:06:10 2026        deployed        app-6-10-chart-0.1.0    1.0
   Upgrade complete
```

Проверим Под еще раз:
```bash
$ kubectl get pods
NAME                        READY   STATUS    RESTARTS          AGE
app-6-10-564b76fdb5-x4625   1/1     Running   0                 15m
```

Мы видим, что Под тот же, что был создан при первой сборке. Это обеспечивается идемпотентностью ```k8s``` - если желаемое состояние совпадает с текущим, то ресурсы не пересоздаются.
