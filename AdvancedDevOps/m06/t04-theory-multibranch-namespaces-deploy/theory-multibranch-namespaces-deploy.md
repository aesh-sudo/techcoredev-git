Когда разработку ведет команда, при деплое изменений могут возникнуть проблемы:
* Конфликты имен ресурсов. Например:<br>
Конфликт имен релизов: имя релиза уникально в пределах ```namespace```, поэтому в общем ```namespace``` две ветки не смогут задеплоить релиз с одним именем (например, ```my-app```). Отдельные ```namespace``` решат эту проблему.
* Смешивание Секретов и ```ConfigMap```.
* Лимиты ```namespace``` делятся на все feature-ветки.
* Фильтрация объектов по веткам – при разборе инцидентов отфильтровать объекты можно только по меткам (```labels```).
* Проблема очистки – если ветка удалена, то сложно определить, какие ресурсы ей принадлежали.

Решение:<br>
Создавать для каждой ветки свой ```namespace```, тогда изолирован будет не только код и история изменений, но и ресурсы.<br>
Для решения задачи в ```Jenkins``` существует специальный вид конфигурации - ```Multibranch Pipeline```:
* Автоматически создает пайплайн для каждой ветки репозитория, в которой есть ```Jenkinsfile```.
* При появлении новой ветки запускает пайплайн.
* Автоматически удаляет пайплайн при удалении ветки.
* Содержит переменную ```BRANCH_NAME``` - имя текущей ветки.

Имя ветки может содержать недопустимые в ```namespace``` символы, поэтому в пайплайне, перед созданием ```namespace``` по имени ветки, его приводят к соответствующему виду.

В пайплайне ```namespace``` должен существовать до ```helm upgrade```. Можно:
* Создать перед деплоем:<br>
```kubectl create namespace <имя_пространства_имен> --dry-run=client -o yaml | kubectl apply -f -```
<br><br>
```--dry-run=client``` – не отправлять сгенерированный запрос на сервер.<br>
```-o yaml``` - вывести результат в формате ```YAML```.<br>
```apply``` – сравнивает желаемое состояние (из ```YAML```) с текущим в кластере, и вносит изменения только при необходимости.<br>
Если бы просто создавали ```namespace```, то при повторном запуске пайплайна процесс завершался с ошибкой, так как ```namespace``` с таким именем уже существует.

* Использовать флаг ```--create-namespace```:<br>
  Пример:
  ```yaml
  helm upgrade --install my-app ./helm-charts/my-app-chart \
  -n feature-auth \
  --create-namespace \
  --set image.tag=${BUILD_NUMBER}
  ```

  ```-n``` – указывает ```namespace``` для деплоя.

Варианты удаления ```namespace``` после соединения feature-ветки с основной и ее удаления:<br>
Автоматически – при удалении ветки, ```Jenkins``` запускает:<br>
```post { cleanup { ... } }```<br>
с<br>
```kubectl delete namespace```

Вручную:<br>
```kubectl delete namespace <имя_пространства_имен>```

По расписанию – в служебном ```namespace``` создается объект ```k8s``` типа ```CronJob```, который запускает приложение для очистки ```namespace```, у которых нет соответствующей ветки в ```Git```.

Пример ```Jenkinsfile```:
```yaml
pipeline {
    agent {
        docker {
            image 'lachlanevenson/k8s-kubectl:v1.25.0'
            args '--entrypoint= --network=minikube'
        }
    }
    environment {
        // Sanitize имени ветки для namespace
        NAMESPACE = env.BRANCH_NAME.replaceAll(/[^a-zA-Z0-9-]/, '-').toLowerCase()
    }
    stages {
        stage('Deploy to feature namespace') {
            steps {
                withCredentials([file(credentialsId: 'minikube-config', variable: 'KUBECONFIG')]) {
                    sh '''
                        curl -fsSL -o helm.tar.gz https://get.helm.sh/helm-v3.14.3-linux-amd64.tar.gz
                        tar -xzf helm.tar.gz
                        export PATH=$PWD/linux-amd64:$PATH
                        
                        # Создаём namespace (если не существует)
                        kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        
                        # Деплоим в namespace
                        helm upgrade --install my-app ./helm-charts/my-app-chart \
                          -n ${NAMESPACE} \
                          --set image.tag=${BUILD_NUMBER}
                    '''
                }
            }
        }
    }
    post {
        cleanup {
            // Когда ветка удалена — удаляем namespace
            script {
                if (env.BRANCH_NAME != 'main') {
                    withCredentials([file(credentialsId: 'minikube-config', variable: 'KUBECONFIG')]) {
                        sh 'kubectl delete namespace ${NAMESPACE} --ignore-not-found'
                    }
                }
            }
        }
    }
}
```

```post { cleanup }``` – выполняется в конце каждой сборки, независимо от результата. В примере, при удалении feature-ветки из репозитория, запускается финальная сборка, при которой ```namespace``` удаляется.
