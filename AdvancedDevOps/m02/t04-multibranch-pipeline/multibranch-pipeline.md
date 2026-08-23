```Multibranch Pipeline``` – тип конфигурации, который:
* Автоматически сканирует все ветки репозитория.
* Создает пайплайн для каждой ветки, в которой есть «Jenkinsfile».
* Автоматически запускает пайплайн при «push» в соответствующую ветку.
* Автоматически удаляет пайплайн при удалении ветки.

Каждая ветка – отдельный пайплайн со своей историей, артефактами и логами.

В «GitHub» создадим репозиторий «my-app-multibranch» с «Jenkinsfile» в корне.

Клонируем его на хост:
```bash
git clone https://github.com/aesh-sudo/my-app-multibranch.git
```

Создадим базовый «Jenkinsfile» (для ```main```):
```
pipeline {
    agent any

    stages {
        stage('main branch') {
            steps {
                echo 'Branch name: main'
                echo "Build number: ${BUILD_NUMBER}"
            }
        }
    }
}
```

Изменим URL-адрес удаленного репозитория ```origin``` (стандартное имя основного репозитория, с которого клонировали проект), чтобы он указывал на SSH-адрес (SSH-соединение с «GitHub» уже настроено).

Сделаем «commit» и «push» в «main»:
```bash
git add Jenkinsfile
git commit -m "feat: add Jenkinsfile for main branch"
git push origin main
```

Создадим ветку ```feature/login```:
```bash
git checkout -b feature/login
```

Со своей версией «Jenkinsfile»:
```
pipeline {
    agent any

    stages {
        stage('feature/login branch') {
            steps {
                echo 'Branch name: feature/login'
                echo "Build number: ${BUILD_NUMBER}"
            }
        }
    }
}
```

Сделаем «commit» и «push» в «feature/login»:
```bash
git add Jenkinsfile
git commit -m "feat: add Jenkinsfile for login feature"
git push origin feature/login
```

Вернемся на «main» и создадим ветку ```feature/cart```:
```bash
git checkout main
git checkout -b feature/cart
```

Со своей версией «Jenkinsfile»:
```
pipeline {
    agent any

    stages {
        stage('feature/cart branch') {
            steps {
                echo 'Branch name: feature/cart'
                echo "Build number: ${BUILD_NUMBER}"
            }
        }
    }
}
```

Сделаем «commit» и «push» в «feature/cart»:
```bash
git add Jenkinsfile
git commit -m "feat: add Jenkinsfile for cart feature"
git push origin feature/cart
```

Проверим структуру репозитория:
```bash
$ git branch -a
* feature/cart
  feature/login
  main
  remotes/origin/feature/cart
  remotes/origin/feature/login
  remotes/origin/main
```

В «UI Jenkins» создадим конфигурацию с именем «my-app-multibranch» и типом ```Multibranch Pipeline```.<br>
Настройки:<br>
Секция ```Branch Sources```:<br>
Нажмем ```Add source```, выберем ```Git``` и заполним параметр:<br>
```Project Repository``` (репозиторий проекта):
```
https://github.com/aesh-sudo/my-app-multibranch.git
```

Секция ```Build Configuration```:<br>
```Mode``` (режим):
```
by Jenkinsfile
```
```Script Path``` (путь к «Jenkinsfile»):
```
Jenkinsfile
```

После сохранения конфигурации «Jenkins» автоматически запустит сканирование репозитория и сборку в каждой ветке, где есть «Jenkinsfile».

Перейдем в ветку «feature/login» и внесем изменение в «Jenkinsfile»:
```
pipeline {
    agent any

    stages {
        stage('feature/login branch') {
            steps {
                echo 'Branch name: feature/login CHANGE'
                echo "Build number: ${BUILD_NUMBER}"
            }
        }
    }
}
```

Сделаем «commit» и «push» в «feature/login»:
```bash
git add Jenkinsfile
git commit -m "feat: update Jenkinsfile"
git push origin feature/login
```

Перейдем в «UI Jenkins» и запустим сканирование.
У ветки «feature/login» изменится номер сборки (```2```), а у остальных веток останется прежним, так как в них изменений не было.
