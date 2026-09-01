В каталоге задачи создадим файл пайплайна «.gitlab-ci.yml»:
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
```

```stages``` – этапы выполнения.<br>
```test``` – имя джобы.<br>
```stage: test``` – этап, которому принадлежит джоба.<br>
```image``` – контейнер, в котором будет выполнена джоба.<br>
```script``` – команды для выполнения.

Последовательность выполнения:<br>
«GitLab» создаст джобу «test» из одноименного этапа и отправит ее раннеру. Раннер создаст контейнер, внутри которого будут выполнены заданные в джобе команды. Результат будет отправлен в «GitLab».

Скопируем этот файл в каталог с приложением (~/projects/my-app), перейдем в него и отправим изменения в «GitLab»:
```bash
git add .gitlab-ci.yml
git commit -m "feat: add .gitlab-ci.yml with test job"
git push origin main
```

В «GitLab» пайплайн отработает с ошибкой, так как для скачивания образа «Python» необходим «Executor» типа «Docker».<br>
Удалим регистрацию раннера:
```bash
docker exec -it gitlab-runner gitlab-runner unregister --name my-first-runner
```

Перерегистрируем раннер с нужным «Executor»:
```bash
docker exec -it gitlab-runner gitlab-runner register \
  --url http://gitlab.aesh.com:8929 \
  --registration-token токен, полученный при создании раннера в GitLab \
  --executor docker \
  --docker-image alpine:latest \
  --description "my-first-runner"
```

Но пайплайн снова отработает с ошибкой, так как в контейнере, который создается для выполнения джобы, нет «Docker».<br>
Для решения проблемы воспользуемся подходом, при котором контейнер использует «Docker», установленный на хосте.<br>
Пересоздадим раннер с пробросом «docker.sock»:
```
services:
  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    container_name: gitlab-runner
    restart: always
    extra_hosts:
      - "gitlab.aesh.com:host-gateway"
    volumes:
      - 'runner_config:/etc/gitlab-runner'
      - '/var/run/docker.sock:/var/run/docker.sock'

volumes:
  runner_config:
```

Пайплайн снова отработает с ошибкой, так как раннер не может подключиться к «GitLab» для клонирования репозитория.

Проверим, какая сеть создалась при создании контейнера с «GitLab»:
```bash
$ docker inspect gitlab -f '{{json .NetworkSettings.Networks}}' | python3 -m json.tool
gitlab-install_default
```

Проверим, какая сеть создалась при создании контейнера с раннером:
```bash
$ docker inspect gitlab-runner -f '{{json .NetworkSettings.Networks}}' | python3 -m json.tool
t03-create-gitlab-ci-yml-and-test-job_default
```

Разные сети не могут общаться между собой.<br>
Включим раннер в сеть контейнера с «GitLab» и исключим его из сети, созданной при создании раннера, а затем удалим эту сеть:
```bash
$ docker network connect gitlab-install_default gitlab-runner
$ docker network disconnect t03-create-gitlab-ci-yml-and-test-job_default gitlab-runner
$ docker network rm t03-create-gitlab-ci-yml-and-test-job_default
```

Пайплайн снова отработает с ошибкой, так как контейнер-исполнитель будет также создан с другой сетью и не будет иметь доступа к «GitLab». Чтобы включить контейнер-исполнитель в общую сеть, необходимо указать эту сеть при регистрации раннера. Удалим регистрацию раннера и зарегистрируем его с необходимыми данными:
```bash
docker exec -it gitlab-runner gitlab-runner unregister --name my-first-runner

docker exec -it gitlab-runner gitlab-runner register \
  --url http://gitlab.aesh.com:8929 \
  --registration-token токен, полученный при создании раннера в GitLab \
  --executor docker \
  --docker-image alpine:latest \
  --description "my-first-runner" \
  --docker-network-mode gitlab-install_default
```
