### Задача (Настройка): Создать аккаунт на hub.docker.com (или использовать GHCR/GitLab Registry). ###
Будем использовать «GHCR».<br>
«GitHub Packages» поддерживает проверку подлинности только с помощью «personal access token (classic)».<br>
Инструкция по созданию «PAT» описана в документации «GitHub». Создадим «PAT» и зададим его области применения:<br>
```read:packages``` – для выгрузки и установки пакетов из репозитория «GitHub Packages».<br>
```write:packages``` – для загрузки и публикации пакетов из репозитория «GitHub Packages».<br>
```delete:packages``` - для удаления пакетов из репозитория «GitHub Packages».

Лучше скопировать токен и сохранить, так как в «GitHub» он будет показан один раз (при создании).

В терминале войдем в службу регистрации контейнеров (инструкция также описана в документации «GitHub»):
```bash
export CR_PAT=YOUR_TOKEN
$ echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
Login Succeeded
```
```USERNAME``` – логин в «GitHub».

Команда выхода из аккаунта:
```bash
docker logout ghcr.io
```

### Задача (Secrets): Создать Access Token. Добавить его в GitHub Secrets (в настройках репозитория): DOCKER_USERNAME и DOCKER_PASSWORD. ###
В репозитории «GitHub» заходим в «Settings (Настройки)». В левой панели находим «Secrets and variables (Секреты и переменные)» и выбираем пункт «Actions (Действия)». Создадим секреты:<br>
```DOCKER_USERNAME``` – логин «GitHub».<br>
```DOCKER_PASSWORD``` – токен (PAT), который создали в предыдущей задаче.
