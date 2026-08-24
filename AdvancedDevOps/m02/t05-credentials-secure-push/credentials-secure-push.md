```Jenkins Credentials``` – специальное защищенное хранилище для секретов.<br>
Преимущества секретов:
* Зашифрованы.
* Не попадают в «Git».
* Маскируются в логах.
* Доступ можно разграничивать.

Создадим «Credentials» в «Jenkins»:<br>
В «UI Jenkins» выберем меню:
```
Manage Jenkins – Credentials - Add Credentials
```
Выберем тип создаваемых данных:
```
Username with password
```

```Scope``` (масштаб использования учетных данных):
```
Global (Jenkins, nodes, items, all child items, etc)
```

```Username``` – так как мы хотим сохранить образ в «Docker Hub», то параметр заполним именем пользователя «Docker Hub».

```Password``` – пароль учетной записи в «Docker Hub». В примере используем ```PAT``` (```Personal Access Token```), так как:
* Токен можно отозвать в любой момент.
* Токен ограничен по правам – только ```push/pull```.
* Токен уникален только для «Docker Hub».

```ID``` (внутренний уникальный идентификатор) – в примере заполним, так как он будет использован в конфигурации «Jenkinsfile»:
```
docker-hub-credentials
```

```Description``` (описание) – произвольное описание:
```
Docker Hub credentials for pushing images
```

Завершаем создание нажатием кнопки ```Create```.

Синтаксис ```withCredentials```:
```
pipeline {
    agent any
    
    environment {
        // Определяем, где в Jenkinsfile искать Credentials
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        DOCKER_IMAGE_NAME = 'aeshell/my-app-jenkins'
    }
    
    stages {
        stage('Build Image') {
            steps {
                echo "Building Docker image..."
                sh 'docker build -t ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER} .'
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                echo "Pushing image to Docker Hub..."
                
                // withCredentials - безопасное использование секретов
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDENTIALS_ID}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USER}" --password-stdin
                        docker push ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER}
                        docker logout
                    '''
                }
            }
        }
    }
}
```

Параметры:<br>
```credentialsId``` – «ID» «Credentials», данные которого будут использоваться.<br>
```usernameVariable``` – параметр для указания имени переменной окружения, в которую будет помещено значение логина из «Credentials» с указанным «ID».<br>
```passwordVariable``` - параметр для указания имени переменной окружения, в которую будет помещено значение пароля из «Credentials» с указанным «ID».

После выхода из блока ```withCredentials``` переменные автоматически удаляются. В логах значения этих переменных не отображаются.

```--password-stdin``` – при использовании этого параметра пароль принимается из потока ввода, что предотвращает попадание пароля в историю команд оболочки и логи, как в случае использования параметра ```-p```.

Создадим приложение – файл «app.py»:
```python
import os
print(f"Hello from Jenkins build #{os.environ.get('BUILD_NUMBER', 'unknown')}!")
```

Создадим «dockerfile»:
```
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
CMD ["python3", "app.py"]
```

Создадим «Jenkinsfile»:
```
pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'docker-hub-credentials'
        DOCKER_IMAGE_NAME = 'aeshell/my-app-jenkins'
    }

    stages {
        stage('Checkout') {
            steps {
                dir('AdvancedDevOps/m02/t05-credentials-secure-push') {
                    echo 'Code is already checked out'
                }
            }
        }

        stage('Build Image') {
            steps {
                dir('AdvancedDevOps/m02/t05-credentials-secure-push') {
                    echo "Building ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER}"
                    sh 'docker build -t ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER} .'
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo "Pushing to Docker Hub..."

                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDENTIALS_ID}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh '''
                        echo "Logging in as ${DOCKER_USER}..."
                        echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USER}" --password-stdin
                        docker push ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER}
                        docker logout
                    '''
                }
            }
        }

        stage('Done') {
            steps {
                echo "Image ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER} successfully pushed!"
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

Для работы «Pipeline Job» необходимо поместить созданные файлы в «GitHub».

В «UI Jenkins» создадим конфигурацию с именем «m02-t05-pipeline» и типом ```Pipeline```.<br>
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
AdvancedDevOps/m02/t05-credentials-secure-push/Jenkinsfile
```

Сохраним и запустим сборку, нажав «Build Now».
