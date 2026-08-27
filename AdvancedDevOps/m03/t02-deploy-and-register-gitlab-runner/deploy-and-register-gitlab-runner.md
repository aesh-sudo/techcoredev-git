```GitLab Server``` – хранение кода, раздача заданий, прием результатов.<br>
```GitLab Runner``` – получение и выполнение заданий.

Создадим «docker-compose.yml» для «Runner»:
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

volumes:
  runner_config:
```

```extra_hosts``` – выполняет запись в файл ```/etc/hosts``` контейнера, чтобы «Runner» понимал, какой ip-адрес привязан к адресу «GitLab».

```host-gateway``` – ip-адрес хоста «GitLab».

```runner_config:/etc/gitlab-runner``` – волюм для ```config.toml``` (для хранения файла регистрации).

Запустим «Runner»:
```bash
docker compose up -d
```

Проверим логи:
```bash
$ docker logs gitlab-runner
ERROR: Failed to load config stat /etc/gitlab-runner/config.toml: no such file or directory
```

Ошибка говорит о том, что «Runner» еще не зарегистрирован, поэтому нет файла конфигурации.

Проверим, что имя резолвится внутри контейнера:
```bash
$ docker exec gitlab-runner getent hosts gitlab.aesh.com
172.17.0.1      gitlab.aesh.com
```

В «GitLab» получим токен:<br>
Перейдем в меню:
```
Settings - CI/CD - Runners
```
и создадим новый токен (```Create project runner```).<br>
Параметры:<br>
```Run untagged jobs: True``` – брать задания без тегов.

Нажмем ```Create runner``` и в появившейся инструкции по регистрации «Runner» скопируем токен вида:
```
glrt-XXXXXXXXXXXX
```

Регистрация «Runner»:
```
$ docker exec -it gitlab-runner gitlab-runner register
```
```GitLab instance URL: http://gitlab.aesh.com:8929/``` - адрес «GitLab».<br>
```Registration token``` – токен, который получили в «GitLab».<br>
```Name for the runner: my-first-runner``` – имя «Runner» (задается произвольно), которое будет храниться в файле конфигурации «Runner» (```config.toml```).<br>
```Executor: shell``` – исполнитель заданий. Значение ```shell``` - задания выполняются прямо в контейнере «Runner».

Результат:
```
Runner registered successfully. Feel free to start it, but if it's running already the config should be automatically reloaded!
Configuration (with the authentication token) was saved in "/etc/gitlab-runner/config.toml"
```

Проверим результат – посмотрим содержимое конфигурационного файла «Runner» (```config.toml```) в контейнере:
```bash
docker exec gitlab-runner cat /etc/gitlab-runner/config.toml
```

В логах должно появиться сообщение о загрузке конфигурации:
```bash
$ docker logs gitlab-runner 
Configuration loaded
```

Проверим «Runner» в «GitLab»:<br>
Должен появиться «Runner» со статусом (```Status```) «Online».
