Скопируем файлы из M08 и немного подкорректируем «dockerfile»:
```
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

В M08 файлы были размещены по каталогам, а в этой задаче они будут находиться в одном каталоге, поэтому изменили 3 и 5 строки:
```
COPY src/requirements.txt .
COPY requirements.txt .

COPY src/app.py .
COPY app.py .
```
Переключим ```Docker CLI``` на использование Docker-демона внутри ```Minikube VM```:
```bash
eval $(minikube docker-env)
```

Выполним команду ```minikube docker-env``` отдельно.
```bash
$ minikube docker-env
export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://192.168.49.2:2376"
export DOCKER_CERT_PATH="/home/aesh/.minikube/certs"
export MINIKUBE_ACTIVE_DOCKERD="minikube"

# To point your shell to minikube's docker-daemon, run:
# eval $(minikube -p minikube docker-env)
```

Она задает настройки Docker-клиенту хоста, чтобы он подключался к Docker-демону «minikube», а не к локальному.

```$()``` – конструкция выполняет команду внутри скобок и подставляет результат вместо себя.<br>
```eval``` – выполнить строку как команду.

После этого любая команда «docker» будет использовать данные демона внутри «Minikube VM».

Для возврата к предыдущим настройкам «Docker» необходимо выполнить команду:
```bash
eval $(minikube docker-env -u)
```
```-u (unset)``` – вернет команды для удаления переменных окружения «minikube» с хоста.

Теперь соберем образ приложения:
```bash
$ docker build -t my-app:k8s .
unset

Проверим, появился ли образ:
```bash
$ docker images
                                                                                          i Info →   U  In Use
IMAGE                                             ID             DISK USAGE   CONTENT SIZE   EXTRA
my-app:k8s                                        7d6c3455122a        133MB             0B
```
