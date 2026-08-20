```Pipeline as Code``` – подход к реализации непрерывной интеграции и доставки, при котором описание конвейера сборки хранится в виде кода (```Jenkinsfile```) в репозитории, а не настраивается через ```UI Jenkins```.

Эволюция подходов:<br>
```Freestyle Jobs```:
* Конфигурация в «XML» на сервере «Jenkins».
* Управление через «UI».
* Отсутствие версионирования.

```Pipeline as Code```:
* Конфигурация в файле «Jenkinsfile» в «Git».
* Управление через код.
* Полное версионирование.

Синтаксисы:<br>
Декларативный (```Declarative```) – строгий, структурированный. Подходит для описания стандартных процессов.<br>
Скриптовый (```Scripted```) – свободный (```Groovy```). Подходит для описания сложных сценариев.

В приложении используется ```Python```, а в образе ```jenkins/jenkins:lts``` он не установлен:
```bash
$ docker exec jenkins python3 --version
OCI runtime exec failed: exec failed: unable to start container process: exec: "python3": executable file not found in $PATH
$ docker exec jen-kins pip --version
OCI runtime exec failed: exec failed: unable to start container process: exec: "pip": executable file not found in $PATH
```

Создадим «dockerfile» для образа «Jenkins» с «Python»:
```
FROM jenkins/jenkins:lts

# Переключимся на root для установки пакетов
USER root

# Установим Python3, pip и venv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Возвратимся к пользователю jenkins (безопасность)
USER jenkins
```

Соберем образ:
```bash
docker build -t jenkins-python:lts .
```

Остановим и удалим контейнер с «Jenkins» и запустим контейнер с «Jenkins» на основе образа, который создали:
```bash
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins jenkins-python:lts
```

Проверим еще раз наличие «Python» в контейнере с «Jenkins»:
```bash
$ docker exec jenkins python3 --version
Python 3.13.5
$ docker exec jenkins python3 -m pip --version
pip 25.1.1 from /usr/lib/python3/dist-packages/pip (python 3.13)
```

Создадим файл приложения – «app.py»:
```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
```

Создадим файл с тестами приложения – «test_app.py»:
```python
from app import add, subtract

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    assert subtract(-1, -1) == 0
```

Создадим файл с зависимостями – «requirements.txt»:
```python
pytest==7.4.0
```

Создадим «Jenkinsfile»:
```
pipeline {
    // Определяем, где запускать пайплайн
    agent any

    // Описание пайплайна
    stages {
        // Этап 1: Установка зависимостей
        stage('Install Dependencies') {
            steps {
                dir('AdvancedDevOps/m02/t02-pipeline-as-code-jenkinsfile') {
                        echo 'Installing Python dependencies...'
                        sh 'python3 -m venv venv'
                        sh './venv/bin/pip install -r requirements.txt'
                }
            }
        }

        // Этап 2: Запуск тестов
        stage('Test') {
            steps {
                dir('AdvancedDevOps/m02/t02-pipeline-as-code-jenkinsfile') {
                        echo 'Running tests with pytest...'
                        sh './venv/bin/python -m pytest -v'
                }
            }
        }

        // Этап 3: Финальное сообщение
        stage('Done') {
            steps {
                echo 'All tests passed successfully!'
            }
        }
    }
}
```

```pipeline``` - ключевое слово, обозначающее декларативный пайплайн.<br>
```agent any``` - использовать любой доступный агент (```worker```). В примере это сам Jenkins-сервер.<br>
```stages``` - контейнер для всех этапов.<br>
```stage``` - логическая единица работы. Имя видно в «UI Jenkins».<br>
```steps``` - команды, выполняемые в этапе.

```python3 -m venv venv``` – создание каталога ```./venv``` с копией «Python» и «pip».<br>
```./venv/bin/pip install -r requirements.txt``` – установка зависимостей в каталог ```./venv```.<br>
```./venv/bin/python -m pytest -v``` – запуск ```pytest``` из ```./venv```.

Команды ```sh``` выполняются в корне ```workspace```, куда, при запуске сборки, клонируется репозиторий. Но файлы приложения находятся не в корне, поэтому необходимо указать «Jenkins», где их искать. Для этого предназначен блок ```dir()```, который меняет рабочую директорию для всех команд, расположенных внутри него.<br>
Блоки ```dir()``` можно вкладывать друг в друга, а также использовать несколько блоков ```dir()``` в одном ```stage```.

Имя файла «Jenkins» должно начинаться с большой буквы и быть без расширения.

Для работы «Pipeline Job» необходимо поместить созданные файлы в «GitHub».

В «UI Jenkins» создадим конфигурацию с именем «m02-t02-pipeline» и типом ```Pipeline```.<br>
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
AdvancedDevOps/m02/t02-pipeline-as-code-jenkinsfile/Jenkinsfile
```

Запустим сборку, нажав «Build Now».
