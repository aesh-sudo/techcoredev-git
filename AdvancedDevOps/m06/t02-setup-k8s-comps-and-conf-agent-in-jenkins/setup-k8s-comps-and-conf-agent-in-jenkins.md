Откроем меню:<br>
```Manage Jenkins (Настройки) – Plugins - Available plugins```<br>
Увидим список плагинов, доступных для установки. Найдем и установим плагины:
* ```Kubernetes``` - позволяет ```Jenkins``` управлять ```k8s```: запускать агентов (```runners```) как Поды внутри кластера, объявлять облачные подключения.
* ```Kubernetes CLI``` – автоматически настраивает ```kubectl``` внутри ```job``` для управления кластером. Шаг ```withKubeConfig``` в ```Jenkinsfile``` - автоматическая настройка ```kubectl``` из ```credentials```.

##########

Посмотрим данные файла ```~/.kube/config```:
```
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /home/aesh/.minikube/ca.crt
    extensions:
    - extension:
        last-update: Fri, 18 Sep 2026 00:11:48 UTC
        provider: minikube.sigs.k8s.io
        version: v1.38.1
      name: cluster_info
    server: https://192.168.49.2:8443
  name: minikube
contexts:
- context:
    cluster: minikube
    extensions:
    - extension:
        last-update: Fri, 18 Sep 2026 00:11:48 UTC
        provider: minikube.sigs.k8s.io
        version: v1.38.1
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

```server``` – адрес API-сервера кластера.<br>
```certificate-authority / client-certificate / client-key``` – пути к файлам сертификатов на хосте.

Необходимо дать ```Jenkins``` безопасный доступ к кластеру. Для этого добавим файл ```~/.kube/config``` в ```Jenkins``` как ```credential```. Он будет храниться в зашифрованном виде, а пайплайн сможет получить к нему доступ через ```withCredentials```.

В ```UI Jenkins``` выберем меню:<br>
```Manage Jenkins – Credentials - Add Credentials```<br>
Выберем тип создаваемых данных:<br>
```Secret file```

```Scope``` (масштаб использования учетных данных):<br>
```Global (Jenkins, nodes, items, all child items, etc)```

```File``` (файл, который необходимо поместить в ```Credentials```):<br>
Помещаем файл ```~/.kube/config```, предварительно скопировав его в удобное для выбора место.

```ID``` (внутренний уникальный идентификатор / имя):<br>
```minikube-config```

```Description``` (описание) – произвольное описание:<br>
```kubeconfig for Minikube```

Завершаем создание нажатием кнопки ```Create```.

##########

В ```Jenkinsfile``` секция ```agent``` указывает, где должны выполняться этапы пайплайна:
* ```agent any``` - использовать любой доступный агент (```worker```).
* ```agent none``` – агент задается не на уровне пайплайна, а на уровне отдельных ```stage```.
* ```agent { docker { image '...' } }``` – пайплайн или отдельные ```stage``` выполняются внутри Docker-контейнера.
* ```agent { kubernetes { yaml '...' } }``` - пайплайн или отдельные ```stage``` выполняются внутри Пода, который будет развернут в кластере.

Для работы Docker-агента необходимо дополнительно установить плагин ```Docker Pipeline```.

Создадим минимальный ```Jenkinsfile``` для проверки работы агента:
```
pipeline {
    agent {
        docker {
            image 'lachlanevenson/k8s-kubectl:v1.25.0'
            args '--entrypoint='
        }
    }
    stages {
        stage('Verify kubectl') {
            steps {
                sh 'kubectl version --client'
                sh 'echo "Agent работает в контейнере с kubectl!"'
            }
        }
    }
}
```

```agent { docker { image '...' } }``` – ```Jenkins``` поднимет контейнер с указанным образом перед пайплайном, примонтирует в него ```workspace``` и удалит после завершения.

```args '--entrypoint='``` – очистка ```entrypoint```, прописанного в образе, чтобы он не конфликтовал с ```entrypoint```, который передает ```Jenkins```.

```sh 'kubectl version --client'``` – команда для проверки клиента внутри контейнера агента.

В ```Jenkins``` создадим конфигурацию для проверки агента.<br>
Имя: ```test-agent```.<br>
Тип: ```Pipeline```.

Настройки конфигурации:<br>
```Definition```: ```Pipeline script```.<br>
```Script```: вставим содержимое файла ```Jenkinsfile```.

И сохраним конфигурацию.

Запуск сборки:<br>
На странице сборки в левом меню необходимо выполнить команду ```Build Now```.

Просмотр логов сборки:<br>
Нажать на номер сборки (например, ```#1```) и выбрать пункт меню ```Console Output```.

Во время выполнения пайплайна появилось СОО – ```Jenkins``` пытается развернуть в контейнере образ, но в контейнере нет демона ```Docker```.<br>
Для решения проблемы воспользуемся подходом, при котором контейнер использует ```Docker```, установленный на хосте.

Пересоздадим контейнер с пробросом ```docker.sock```:
```bash
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home
 -v /var/run/docker.sock:/var/run/docker.sock --name jenkins jenkins/jenkins:lts
```

На хосте получим ```GID``` группы ```docker```:
```bash
$ getent group docker | cut -d: -f3
986
```

Внутри контейнера создадим группу ```docker``` с таким же ```GID``` и добавим в нее пользователя ```jenkins```:
```bash
# groupadd -g 986 docker
# usermod -aG docker jenkins
```

Перезапустим контейнер с ```Jenkins```:
```bash
docker restart jenkins
```

Также установим в контейнер ```Docker CLI```:
```bash
docker exec -u root jenkins bash -c '
    curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-29.6.0.tgz -o /tmp/docker.tgz &&
    tar -xzf /tmp/docker.tgz -C /tmp &&
    mv /tmp/docker/docker /usr/local/bin/docker &&
    chmod +x /usr/local/bin/docker &&
    rm -rf /tmp/docker /tmp/docker.tgz'
```

Проверим результат установки:
```bash
$ docker exec jenkins docker --version
Docker version 29.6.0, build fb59821
```

В ```Jenkins UI``` еще раз запустим сборку и посмотрим логи:
```
+ kubectl version --client
WARNING: This version information is deprecated and will be replaced with the output from kubectl ver-sion
 --short.  Use --output=yaml|json to get the full version.
Client Version: version.Info{Major:"1", Minor:"25", GitVersion:"v1.25.0",
 GitCommit:"a866cbe2e5bbaa01cfd5e969aa3e033f3282a8a2", GitTreeState:"clean",
 BuildDate:"2022-08-23T17:44:59Z", GoVersion:"go1.19", Compiler:"gc", Platform:"linux/amd64"}
Kustomize Version: v4.5.7
[Pipeline] sh
+ echo 'Agent работает в контейнере с kubectl!'
Agent работает в контейнере с kubectl!
```
