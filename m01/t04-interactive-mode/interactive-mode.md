```bash
$ docker run -it ubuntu bash
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
d1f56e4c7f2f: Pull complete
81e2f2053c8f: Pull complete
107e4f1717f2: Download complete
Digest: sha256:53958ec7b67c2c9355df922dd08dbf0360611f8c3cdb656875e81873db9ffdba
Status: Downloaded newer image for ubuntu:latest
root@bd1b5ed69761:/#
```
```-it``` – запуск контейнера в интерактивном режиме. Сочетание параметров:<br>
```-i``` - оставляет стандартный ввод (STDIN) открытым.<br>
```-t``` – подключает к контейнеру виртуальный терминал (TTY) для ввода команд.<br>

Выполняется скачивание последнего актуального (```latest```) образа ```ubuntu:latest``` (если его нет) из репозитория, запускается контейнер и выполняется вход во внутреннее пространство контейнера.
