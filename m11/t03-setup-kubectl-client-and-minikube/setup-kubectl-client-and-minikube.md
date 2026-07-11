### Задача (Установка): Установить kubectl (CLI для K8s). ###

```kubectl``` – утилита (клиент) командной строки для управления кластером/кластерами «Kubernetes» локально или удаленно. Версия ```kubectl``` может отличаться от версии кластера на одну минорную версию.<br>
Пример:<br>
1.35.2<br>
1 – главная (major) версия.<br>
35 – подверсия (minor) версия.<br>
2 – патч (patch) версия.

Команды по установке ```kubectl``` можно найти в документации на сайте «Kubernetes».

Проверка установленной версии:
```bash
$ kubectl version --client
Client Version: v1.36.2
Kustomize Version: v5.8.1
```

### Задача (Установка): Установить minikube (Локальный K8s-кластер для разработки). ###

В документации на сайте «Kubernetes» можно найти раздел, в котором есть ссылка на сайт «minikube». На странице загрузки необходимо задать параметры платформы, на которую необходимо установить приложение, и способ загрузки.
Также на странице загрузки указаны требования, которые необходимо выполнить перед запуском «minikube».

Проверка версии установленного «minikube»:
```bash
$ minikube version
minikube version: v1.38.1
commit: c93a4cb9311efc66b90d33ea03f75f2c4120e9b0
```

### Задача (Запуск): Запустить Minikube: minikube start. ###
```bash
minikube start
```

Информация установки:<br>
Версия «Kubernetes», используемая в «minikube»:
```
Downloading Kubernetes v1.35.1 preload
```

«kubectl» был автоматически настроен для использования локального кластера «minikube»:
```
kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

Так как «kubectl» настроил связь с кластером «minikube», то можно проверить их версии:
```bash
$ kubectl version
Client Version: v1.36.2      1
Kustomize Version: v5.8.1
Server Version: v1.35.1      2
```

```1``` – версия «kubectl» (клиента).<br>
```2``` – версия кластера «minikube».

В «minikube» есть встроенная утилита «kubectl», но она не подойдет для взаимодействия с удаленными кластерами.

### Задача (Проверка): Проверить кластер: kubectl get nodes. ###
```bash
$ kubectl get nodes
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   29m   v1.35.1
```
