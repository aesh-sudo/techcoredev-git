Создадим «dockerfile» с передачей токена через Аргумент (```ARG```):
```
FROM alpine
ARG PIP_TOKEN=super-secret-token-12345
RUN echo "Using token: $PIP_TOKEN" && echo "pip install from https://token:$PIP_TOKEN@pip.mycompany.com"
CMD ["echo", "Hello from Alpine"]
```

Соберем образ:
```bash
$ docker build -f dockerfile_bad -t my-app-bad .
...
 => [2/2] RUN echo "Using token: super-secret-token-12345" && echo "pip install from
 https://token:super-secret-token-12345@pip.mycompany.com"                                                      0.7s
...
```

В процессе сборки отображено значение аргумента.

Проверим историю слоев:
```bash
$ docker history --format "{{.CreatedBy}}" my-app-bad --no-trunc
CMD ["echo" "Hello from Alpine"]
RUN |1 PIP_TOKEN=super-secret-token-12345 /bin/sh -c echo "Using token: $PIP_TOKEN" && echo "pip install from https://token:$PIP_TOKEN@pip.mycompany.com" # buildkit
ARG PIP_TOKEN=super-secret-token-12345
CMD ["/bin/sh"]
ADD alpine-minirootfs-3.24.1-x86_64.tar.gz / # buildkit
```

В слое с аргументом отображено его значение.

```BuildKit Secrets``` - механизм, который:
* Передает секрет только во время выполнения одной команды.
* Секрет не сохраняется в слоях.
* Секрет не виден в истории образа.
* Секрет доступен только в памяти процесса.

Создадим файл «pip_token.txt» в котором сохраним значение Секрета:
```
super-secret-token-12345
```

Создадим «dockerfile» с передачей токена через Секрет (```--mount=type=secret```):
```
FROM alpine

RUN --mount=type=secret,id=pip_token \
    echo "Using token: $(cat /run/secrets/pip_token)" && \
    echo "pip install from https://token:$(cat /run/secrets/pip_token)@pip.mycompany.com"

CMD ["echo", "Hello from Alpine"]
```

```id=pip_token``` – идентификатор Секрета (имя).<br>
```/run/secrets/pip_token``` – путь к Секрету внутри контейнера.

Путь к Секрету внутри контейнера по умолчанию задается шаблоном:
```
/run/secrets/идентификатор_секрета
```

```--target``` – параметр внутри ```--mount``` для изменения точки монтирования Секрета внутри контейнера.

Соберем образ:
```bash
$ docker build --secret id=pip_token,src=pip_token.txt -f dockerfile_good -t my-app-good .
...
 => [stage-0 2/2] RUN --mount=type=secret,id=pip_token     echo "Using token: $(cat /run/secrets/pip_token)"
 &&     echo "pip install from https://token:$(cat /run/secrets/pip_token)@pip.mycompa  0.7s
...
```

```--secret id=pip_token,src=pip_token.txt``` – чтение значения Секрета из файла ```pip_token.txt``` и назначение ему идентификатора (имени) ```pip_token```.

В процессе сборки значение Секрета не отображено.

Проверим историю слоев:
```bash
$ docker history --format "{{.CreatedBy}}" my-app-good --no-trunc
CMD ["echo" "Hello from Alpine"]
RUN /bin/sh -c echo "Using token: $(cat /run/secrets/pip_token)" &&     echo "pip install from
 https://token:$(cat /run/secrets/pip_token)@pip.mycompany.com" # buildkit
CMD ["/bin/sh"]
ADD alpine-minirootfs-3.24.1-x86_64.tar.gz / # buildkit
```

В слое с Секретом его значения не отображено.
