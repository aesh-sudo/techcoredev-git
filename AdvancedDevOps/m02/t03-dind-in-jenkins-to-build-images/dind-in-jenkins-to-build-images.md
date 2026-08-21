```Docker``` – клиент-серверная архитектура:<br>
```Daemon``` (сервер/демон) – выполняет команды.<br>
```CLI``` (клиент) – отдает команды демону.<br>
```/var/run/docker.sock``` – Unix-сокет, через который демон слушает запросы клиента.

Контейнер изолирован и в нем не установлен «Docker», поэтому команда:
```
sh 'docker ps'
```
 внутри контейнера не выполняется и выдает СОО:
 ```
docker: command not found
```

Для решения проблемы воспользуемся подходом, при котором контейнер использует «Docker», установленный на хосте.

Пересоздадим контейнер с пробросом ```docker.sock```:
```bash
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home
 -v /var/run/docker.sock:/var/run/docker.sock --name jenkins jenkins-python:lts
```

```-v /var/run/docker.sock:/var/run/docker.sock``` – монтируем сокет хоста в контейнер по аналогичному пути.

Проверим наличие файла сокета внутри контейнера:
```bash
$ docker exec jenkins ls -la /var/run/docker.sock
srw-rw---- 1 root 986 0 Aug 20 10:36 /var/run/docker.sock
```

Права ```rw``` есть только у пользователя «root» и группы «986».

Установим «Docker CLI» в контейнер:
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

Попробуем выполнить команду:
```bash
$ docker exec jenkins docker ps
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```
Проверим пользователей в контейнере:
```bash
$ docker exec jenkins id
uid=1000(jenkins) gid=1000(jenkins) groups=1000(jenkins)
```

Причина:<br>
В контейнере один пользователь – «jenkins». Сокет принадлежит пользователю «root» и группе «986». У пользователя «Jenkins» этой группы нет, поэтому доступ запрещен.

Решение:<br>
Добавим пользователя «jenkins» в группу «986».

Создадим в контейнере группу, аналогичную группе сокета на хосте:
```bash
docker exec -u root jenkins groupadd -f -g 986 docker
```

Добавим пользователя «jenkins» в эту группу:
```bash
docker exec -u root jenkins usermod -aG docker jenkins
```

Перезапустим контейнер, чтобы группы применились к процессам:
```bash
docker restart jenkins
```

Еще раз проверим пользователей в контейнере:
```bash
$ docker exec jenkins id
uid=1000(jenkins) gid=1000(jenkins) groups=1000(jenkins),986(docker)
```

Также можно проверить список запущенных контейнеров:
```bash
docker exec jenkins docker ps
```

Команда выведет список запущенных контейнеров хоста, так как команды выполняет демон хоста.

Создадим «Jenkinsfile» для проверки:
```
pipeline {
    agent any

    stages {
        stage('Docker Check') {
            steps {
                echo 'Checking Docker availability...'
                sh 'docker --version'
                sh 'docker ps'
            }
        }
    }
}
```

В «UI Jenkins» создадим конфигурацию с именем «m02-t03-pipeline» и типом ```Pipeline```.<br>
Настройки:<br>
Секция ```Pipeline```:<br>
```Definition``` – выбираем значение ```Pipeline script from SCM```.<br>
```SCM``` - выбираем пункт ```Git``` и заполняем поле:<br>
```Repository URL``` (адрес репозитория):
```
https://github.com/aesh-sudo/techcoredev-git.git
```

```Branches to build``` – ветка/ветки репозитория для сборки «Jenkins»:
```
*/main
```

```Script Path``` – так как «Jenkinsfile» находится не в корне репозитория, то укажем путь к нему:
```
AdvancedDevOps/m02/t03-dind-in-jenkins-to-build-images/Jenkinsfile
```

Сохраним и запустим сборку, нажав «Build Now».<br>
Задача 7 решена.

Скопируем в каталог задачи файлы приложения (из прошлой задачи):
```
app.py
requirements.txt
test_app.py
```

Добавим этап сборки образа в пайплайн – файл «Jenkinsfile»:
```
pipeline {
    agent any

    stages {
        stage('Docker Check') {
            steps {
                echo 'Checking Docker availability...'
                sh 'docker --version'
                sh 'docker ps'
            }
        }

        stage('Build Image') {
            steps {
                dir('AdvancedDevOps/m02/t03-dind-in-jenkins-to-build-images') {
                    echo 'Building Docker image...'
                    sh 'docker build -t my-app-jenkins:${BUILD_NUMBER} .'
                }
            }
        }
    }
}
```

```BUILD_NUMBER``` – встроенная переменная «Jenkins», которая автоматически подставляется при каждом запуске сборки. Также существуют и другие встроенные переменные. Полный список доступен по адресу:
```
[адрес_Jenkins]/env-vars.html
```

Создадим «dockerfile» для сборки образа приложения:
```
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY app.py test_app.py ./

CMD ["python3", "-m", "pytest", "-v"]
```

Для работы «Pipeline Job» необходимо поместить созданные файлы в «GitHub».

В «UI Jenkins» запустим конфигурацию «m02-t03-pipeline» еще раз.

Проверим результат – наличие образа:
```bash
$ docker images
                                                                                          i Info →   U  In Use
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
my-app-jenkins:3     270bf6b50f3d        208MB         50.6MB
```

Запустим созданный образ:
```bash
$ docker run --rm my-app-jenkins:3
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.0, pluggy-1.6.0 -- /usr/local/bin/python3
cachedir: .pytest_cache
rootdir: /app
collecting ... collected 2 items

test_app.py::test_add PASSED                                             [ 50%]
test_app.py::test_subtract PASSED                                        [100%]

============================== 2 passed in 0.02s ===============================
```

Пояснение:<br>
«Jenkins» клонировал заданный репозиторий. С помощью конструкции ```dir()``` перешел в каталог с «dockerfile» и получил заданную в «Jenkinsfile» команду:
```bash
docker build -t my-app-jenkins:3 .'
```
Через сокет ```docker.sock``` передал ее демону на хосте. Демон выполнил команду.
