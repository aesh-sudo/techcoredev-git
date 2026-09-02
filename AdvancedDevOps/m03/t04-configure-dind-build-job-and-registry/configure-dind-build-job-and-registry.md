DinD-режим требует использования раннера в привилегированном режиме, который включается только путем изменения параметра в конфигурационном файле раннера:
```
...
[runners.docker]
  privileged = true
...
```

Перезагрузим раннер:
```bash
docker restart gitlab-runner
```

Чтобы включить «Container Registry» в «GitLab», необходимо в секции «GITLAB_OMNIBUS_CONFIG» конфигурации «GitLab» добавить свойство:
```
registry_external_url 'http://gitlab.aesh.com:5050'
```
А также указать порт в секции «ports»:
```
5050:5050
```
И пересоздать контейнер с «GitLab»:
```bash
docker compose down
docker compose up -d
```

Проверить «GitLab» можно после появления результата при отслеживании логов контейнера «GitLab» в реальном времени:
```bash
$ docker compose logs -f | grep -i reconfigured
gitlab  | gitlab Reconfigured!
```

Если в «GitLab» появилась страница:
```
Deploy - Package registry
```
значит «GitLab Registry» настроен.

Добавим джобу «build» в одноименный этап пайплайна – файл «.gitlab-ci.yml»:
```
stages:
  - test
  - build

test:
  stage: test
  image: python:3.10-slim
  script:
    - pip install -r requirements.txt
    - pytest

build:
  stage: build
  image: docker:latest
  services:
    - name: docker:dind
      command: ["--insecure-registry=gitlab.aesh.com:5050"]
  variables:
    DOCKER_HOST: tcp://docker:2375
    DOCKER_TLS_CERTDIR: ""
    DOCKER_BUILDKIT: "0"
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_JOB_TOKEN $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

```services: [docker:dind]``` - запускает service-контейнер параллельно с build-контейнером.

```command: ["--insecure-registry=gitlab.aesh.com:5050"]``` – «Registry» работает через «HTTP», так как мы отключили использование «TLS». Но клиент «Docker» по умолчанию использует «HTTPS» для соединения с «Registry».<br>
Настройка отключает использование «HTTPS» при соединении с указанным «Registry».

```DOCKER_HOST: tcp://docker:2375``` – адрес демона «Docker», по которому будет подключаться клиент «Docker», запускаемый в джобе.<br>
Пояснение:<br>
При использовании сервиса «DinD», демон «Docker» запускается в отдельном контейнере с именем «docker».<br>
```2375``` – стандартный порт, на котором демон «Docker» слушает TCP-соединения (без «TLS»).

```DOCKER_TLS_CERTDIR: ""``` – отключение «TLS».

```DOCKER_BUILDKIT: "0"``` – отключение нового формата сборки образов – «Docker BuildKit», так как он не поддерживается «Registry», который работает через «HTTP».

Значения следующих переменных задаются автоматически:<br>
```$CI_REGISTRY_USER``` – логин для «Registry». Значение по умолчанию «gitlab-ci-token».<br>
```$CI_JOB_TOKEN``` – токен джобы для аутентификации. Токен действителен только на время выполнения джобы, что повышает безопасность.<br>
```$CI_REGISTRY``` – «URL» «Registry».<br>
```$CI_REGISTRY_IMAGE``` – полный путь к образу. В примере:
```
gitlab.aesh.com:5050/root/my-app
```
```$CI_COMMIT_SHA``` – «SHA» коммита.

В каталоге приложения «~/projects/my-app» создадим «Dockerfile» для сборки образа:
```
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py test_app.py ./
CMD ["python3", "-m", "pytest", "-v"]
```

Отправим изменения в «GitLab»:
```bash
git add .
git commit -m "feat: add build stage with DinD and Registry push"
git push origin main
```

В «GitLab»:<br>
В пайплайне теперь два этапа – «test» и «build».

После отработки пайплайна, в меню:
```
Deploy - Container registry
```
Появился образ с приложением «my-app».
