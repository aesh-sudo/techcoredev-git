```Pipeline as Code``` – подход к реализации непрерывной интеграции и доставки, при котором описание конвейера сборки хранится в виде кода (```Jenkinsfile```) в репозитории, а не настраивается через ```UI Jenkins```.

Эволюция подходов:<br>
```Freestyle Jobs```:
* Конфигурация в «XML» на сервере «Jenkins».
* Управление через «UI».
* Отсутствие версионирования.

```Pipeline as Code```:
* Конфигурация в файле ```Jenkinsfile``` в «Git».
* Управление через код.
* Полное версионирование.

Синтаксисы:<br>
Декларативный (```Declarative```) – строгий, структурированный. Подходит для описания стандартных процессов.<br>
Скриптовый (```Scripted```) – свободный (```Groovy```). Подходит для описания сложных сценариев.

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
```agent any``` — использовать любой доступный агент (```worker```). В примере это сам Jenkins-сервер.<br>
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

Установим «Python» в контейнер с «Jenkins». Для примера достаточно будет установить прямо в контейнер. Если «Python» нужен в контейнере постоянно, то необходимо создать свой образ с ```jenkins/jenkins:lts```, прописав установку «Python» в коде «dockerfile».

Обновим список пакетов:
```bash
docker exec -u root jenkins apt-get update
```

Установим «Python3» и «pip»:
```bash
docker exec -u root jenkins apt-get install -y python3 python3-pip python3-venv
```

Проверим установку:
```bash
$ docker exec jenkins python3 --version
Python 3.13.5
$ docker exec jenkins python3 -m pip --version
pip 25.1.1 from /usr/lib/python3/dist-packages/pip (python 3.13)
```

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
