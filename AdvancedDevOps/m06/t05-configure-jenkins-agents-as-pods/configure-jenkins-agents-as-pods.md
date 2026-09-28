Концепция – по умолчанию в ```Jenkins``` в качестве агентов используются Docker-контейнеры. Настроим архитектуру так, чтобы в качестве агентов выступали Поды внутри кластера ```minikube```.<br>
```Docker Agent```:<br>
Запуск: Docker-контейнер на хосте.<br>
Управление: Docker-демон на хосте.<br>
Масштабирование: на каждую сборку создается свой агент.<br>
Изоляция: контейнерная.<br>
Производственный стандарт: нет.

```k8s Agent```:<br>
Запуск: Под внутри кластера.<br>
Управление: ```k8s``` (```kubelet```).<br>
Масштабирование: много агентов параллельно.<br>
Изоляция: Под и пространство имен (```namespace```).<br>
Производственный стандарт: да.

Преимущества ```k8s Agent``` - автоматическое масштабирование, изоляция через пространство имен, использование ресурсов кластера, не нужен проброс ```docker.sock```.

Направления связи:<br>
```Jenkins``` - ```k8s API```:<br>
```Jenkins``` делает запрос кластеру на создание Пода-агента.<br>
Инструмент: ```kubekonfig```.

Под-агент – ```Jenkins```:<br>
Агент подключается к ```Jenkins``` для получения задач.<br>
Инструмент: ```Jenkins URL``` и ```Jenkins tunnel``` в настройках ```Cloud```.

Так как контейнер ```jenkins``` находится в сети ```bridge```, а ```minikube``` находится в сети ```minikube```, то, для взаимодействия с ```minikube```, включим контейнер ```jenkins``` в сеть ```minikube```:
```bash
docker network connect minikube jenkins
```

Проверим IP-адрес ```jenkins``` в сети ```minikube```:
```bash
$ docker inspect jenkins -f '{{json .NetworkSettings.Networks}}' | python3 -m json.tool
{
    "minikube": {
        "IPAMConfig": {},
        "Links": null,
        "Aliases": [],
        "DriverOpts": {},
        "GwPriority": 0,
        "NetworkID": "43efb2127ada4ecc56095e219a0d9fd399049d08ec6da632d919cf367fa86d39",
        "EndpointID": "f7e2fe5db7d63f4ee13e0a0305148d0b419a47f23778b898824194ad855b70d8",
        "Gateway": "192.168.49.1",
        "IPAddress": "192.168.49.3",
        "MacAddress": "8e:b1:eb:a9:37:77",
        "IPPrefixLen": 24,
        "IPv6Gateway": "",
        "GlobalIPv6Address": "",
        "GlobalIPv6PrefixLen": 0,
        "DNSNames": [
            "jenkins",
            "782847e4c5ec"
        ]
    }
}
```

Проверим связь ```jenkins``` с ```minikube```:
```bash
$ docker exec jenkins curl -sk -o /dev/null -w "Jenkins - K8s API: %{http_code}\n"
 https://192.168.49.2:8443/version
Jenkins - K8s API: 200
```

Под внутри ```minikube``` не может обратиться к контейнеру ```jenkins``` по IP-адресу (```192.168.49.3```) из-за ```Calico```, но может обратиться через ```gateway``` Ноды, на которой запущен (```192.168.49.1```):
```bash
$ kubectl run nettest --rm -it --image=curlimages/curl --restart=Never -- \
  curl -s -o /dev/null -w "Pod - Jenkins: %{http_code}\n" http://192.168.49.1:8080/login
Pod - Jenkins: 200
pod "nettest" deleted from default namespace
```

Для того, чтобы ```Jenkins``` мог создавать Поды внутри кластера, создадим ```RBAC``` (```Role-Based Access Control```) – ролевое управление доступом – файл ```jenkins-sa.yaml```:
```
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jenkins
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: jenkins
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods", "pods/exec", "pods/log", "secrets", "configmaps"]
  verbs: ["*"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: jenkins
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: jenkins
subjects:
- kind: ServiceAccount
  name: jenkins
  namespace: default
```

```ServiceAccount``` – учетная запись для приложений. При запуске агента внутри кластера (Под), ```k8s``` автоматически монтирует к нему токен ```ServiceAccount```, что дает агенту право обращаться к API-серверу ```k8s```. Права учетной записи назначаются через ```Role``` (права) и ```RoleBinding``` (связь ```Role``` и ```ServiceAccount```).

```Role``` – список разрешений.<br>
```apiGroups: [""]``` – основная группа ```k8s```.<br>
```resources``` – список объектов, к которым применяется доступ.<br>
```pods``` – создание и удаление Подов агентов.<br>
```pods/exec``` – выполнение команд внутри Подов.<br>
```pods/log``` – чтение логов Подов.<br>
```secrets``` – секреты.<br>
```configmaps``` – конфигурации.<br>
```verbs: ["*"]``` – разрешены все действия.

```apiGroups: ["apps"]``` – группа ресурсов для управления приложениями.<br>
```resources: ["deployments"]``` – ресурс, к которому применяется доступ.<br>
```verbs``` – действия, которые разрешено выполнять над объектом.

```RoleBinding``` – связь объекта, которому выдаются разрешения, с разрешениями.<br>
```roleRef``` – разрешение.<br>
```subjects``` – объекты, которым выдается разрешение.

Применим ```ServiceAccount```:
```bash
$ kubectl apply -f jenkins-sa.yaml
```

Проверим результаты:
```bash
$ kubectl get sa
NAME      AGE
jenkins   10h

$ kubectl get role
NAME      CREATED AT
jenkins   2026-09-26T11:32:38Z

$ kubectl get rolebinding
NAME      ROLE           AGE
jenkins   Role/jenkins   10h
```

Настроим ```Cloud``` в ```Jenkins```:<br>
```Manage Jenkins - Clouds - New cloud```<br>
```Cloud name``` (имя): ```minikube```.<br>
```Type``` (тип): ```Kubernetes```.

Основные настройки:<br>
```Name```: ```minikube```.<br>
```Kubernetes Namespace```: ```default```.<br>
```Credentials```: ```kubeconfig-selfcontained (kubeconfig for Minikube)```.<br>
```Jenkins URL```: ```http://192.168.49.1:8080```.<br>
```Jenkins tunnel```: ```192.168.49.1:50000```.

Проверим связь с ```k8s```, нажав ```Test Connection```. При удачном соединении будет выведено сообщение:<br>
```Connected to Kubernetes```

Перейдем к настройкам на вкладке ```Pod Templates```:<br>
```Name```: ```jenkins-agent```.<br>
```Namespace```: ```default```.<br>
```Labels```: ```jenkins-agent```.<br>
```Usage```: ```Only build jobs with label expressions matching this node```.<br>
```Service Account```: ```jenkins```.

В ```Jenkins``` создадим новую конфигурацию ```test-k8s-agent``` типа ```Pipeline```:
```
Definition: Pipeline script.
Script:
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
    stages {
        stage('Test K8s Agent') {
            steps {
                sh 'kubectl version --client'
                sh 'echo "Агент работает как Pod в Kubernetes!"'
            }
        }
    }
}
```

```inheritFrom 'jenkins-agent'``` – используем ```Pod template``` из настроек ```Cloud```.

```defaultContainer 'kubectl'``` – sh-шаги по умолчанию выполняются в контейнере ```kubectl```. То есть, в пайплайне, в sh-шагах, конструкцию:<br>
```container('имя_контейнера') { }```<br>
надо использовать, только если шаг необходимо выполнить в другом контейнере.

```yaml'''описание_контейнера'''``` – описание рабочего контейнера ```kubectl```. jnlp-контейнер появится автоматически.

```serviceAccountName: jenkins``` – используем ```ServiceAccount``` с правами, описанный выше.

Сохраним и запустим сборку, нажав ```Build Now```.

Поведение:<br>
```Jenkins``` запрашивает у ```k8s``` создание Пода.<br>
Появляется Под с именем типа ```test-k8s-agent-xxxxx-yyyyy-zzzzz```, который содержит два контейнера: ```jnlp``` (JNLP-протокол для связи с ```Jenkins```) и ```kubectl```.<br>
```jnlp``` подключается к ```Jenkins``` через ```192.168.49.1:50000```.<br>
Пайплайн выполняется внутри контейнера ```kubectl```.<br>
После завершения Под удаляется.
