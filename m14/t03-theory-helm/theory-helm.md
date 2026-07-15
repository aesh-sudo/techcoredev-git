```Helm``` - система управления пакетами для «k8s», выполняющая функции автоматизации создания, конфигурирования и развертывания приложений в кластере.

Основные понятия:<br>
Чарт (```Chart```) - структурированный набор файлов, описывающий связанный набор k8s-ресурсов. Представляет собой упакованное приложение, готовое к развертыванию.

Релиз (```Release```) – экземпляр Чарта, запущенный в кластере «k8s».

Репозиторий (```Repository```) – HTTP-сервер для хранения Чартов.

Состав Чарта:<br>
```Chart.yaml``` – метаданные пакета (имя, версия, описание).<br>
```values.yaml``` – настройки и их значения (пароли, порты, версии).<br>
```templates``` – каталог с шаблонами YAML-файлов (deployment, service, ingress и так далее).

Пример работы:<br>
В шаблоне «deployment.yaml» настройка:
```
port: {{ .Values.containerPort }}
```
```Helm``` читает значение переменной ```containerPort``` из файла ```values.yaml```, подставляет в шаблон и отправляет готовый манифест в «k8s».

Основные команды:<br>
* Добавить репозиторий с Чартами:<br>
Синтаксис:
```bash
helm repo add [NAME] [URL] [flags]
```
Пример:<br>
Добавление официального репозитория «stable».
```bash
helm repo add stable https://charts.helm.sh/stable
```

* Установить Чарт в кластер (создать релиз):<br>
Синтаксис:
```
helm install [NAME] [CHART] [flags]
```
Пример:
```bash
helm install my-release stable/postgresql
```

* Обновить релиз (при изменении настроек):<br>
Синтаксис:
```bash
helm upgrade [RELEASE] [CHART] [flags]
```
Пример:
```bash
helm upgrade my-release stable/postgresql
```

* Откатить релиз к предыдущей версии:<br>
Синтаксис:
```bash
helm rollback <RELEASE> [REVISION] [flags]
```
Пример:
```bash
helm rollback my-release 1
```
