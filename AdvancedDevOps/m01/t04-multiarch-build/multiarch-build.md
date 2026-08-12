Сборщик – версия «BuildKit» с заданными настройками.

Создадим отдельный сборщик с драйвером ```docker-container```, который используется для создания сборщика в отдельном контейнере. Сборщик с таким драйвером может собирать несколько платформ одновременно, но образ нельзя сохранить локально:
```bash
docker buildx create --name container-builder --driver docker-container --bootstrap --use
```

```--bootstrap``` – параметр для запуска сборщика сразу при создании.<br>
```--use``` – параметр для активации сборщика (станет активным по умолчанию).

Посмотрим список сборщиков:
```bash
$ docker buildx ls
NAME/NODE                DRIVER/ENDPOINT                   STATUS    BUILDKIT   
PLATFORMS
container-builder*       docker-container
 \_ container-builder0    \_ unix:///var/run/docker.sock   running   v0.31.2    
linux/amd64 (+2), linux/arm64, linux/arm (+2), linux/ppc64le, (4 more)
default                  docker
 \_ default               \_ default                       running   v0.31.0    
linux/amd64 (+2), linux/arm64, linux/arm (+2), linux/ppc64le, (3 more)
```

Создадим «dockerfile»:
```
FROM alpine
RUN uname -m > /arch
```

Соберем мультиплатформенный образ, но сначала авторизуемся в «Docker Hub»:
```bash
docker login -u aeshell
```

```aeshell``` – имя пользователя в «Docker Hub».

```bash
docker buildx build --platform linux/amd64,linux/arm64 --tag aeshell/my-app:latest --push .
```

Проверим результат:
```bash
$ docker buildx imagetools inspect aeshell/my-app:latest
Name:      docker.io/aeshell/my-app:latest
MediaType: application/vnd.oci.image.index.v1+json
Digest:    sha256:9e352e63958ca85a54c1fb4ceef736fd8020f2d031d31b8c85ff4fdbc3530191

Manifests:
  Name:        docker.io/aeshell/my-app:latest@sha256:
6310cd1b6453f0c73fa4b082e909f9454cfa1094ddbecb2f070b9828b0279ce2
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/amd64

  Name:        docker.io/aeshell/my-app:latest@sha256:
17cfcce3b9dae5dcd72d2aa1a5697e141b16b17b6dd1c64265a93e474d0bf13e
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/arm64

  Name:        docker.io/aeshell/my-app:latest@sha256:
5e855924d30d1ccc81e9123012f1bd080ba0f2d44393fff41d35303a117dac62
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    unknown/unknown
  Annotations:
    vnd.docker.reference.digest: sha256:6310cd1b6453f0c73fa4b082e909f9454cfa1094ddbecb2f070b9828b0279ce2
    vnd.docker.reference.type:   attestation-manifest

  Name:        docker.io/aeshell/my-app:latest@sha256:
1ef69469a8e6bf366da043a92868e4dc444f640c25ec546b1afe95b8ffaf26a0
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    unknown/unknown
  Annotations:
    vnd.docker.reference.digest: sha256:17cfcce3b9dae5dcd72d2aa1a5697e141b16b17b6dd1c64265a93e474d0bf13e
    vnd.docker.reference.type:   attestation-manifest
```

То есть, у нас получилось два образа и две аттестации к ним. Аттестация – информация о том, где и как был собран образ, представленная в JSON-виде.

Проверка запуска с нативной архитектурой:
```bash
$ docker run --rm aeshell/my-app:latest cat /arch
x86_64
```

Чтобы запустить контейнер с ARM-архитектурой на AMD-архитектуре, необходимо зарегистрировать эмулятор ```QEMU``` в ядре.

```binfmt_misc``` – механизм ядра «Linux», который позволяет передавать запускаемое приложение, созданное на другой архитектуре, эмулятору этой архитектуры.

```QEMU User-Mode``` – эмулятор процессора.<br>
Установим ```QEMU``` через контейнер:
```bash
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

```--privileged``` – параметр для предоставления контейнеру полного доступа к системе хоста.<br>
```multiarch/qemu-user-static``` – образ с QEMU-бинарниками.<br>
```--reset``` – параметр для очистки старых правил.<br>
```-p yes``` – зарегистрировать эмуляторы для всех архитектур.

Проверим зарегистрированные эмуляторы:
```bash
ls /proc/sys/fs/binfmt_misc/
```

Правила ```binfmt_misc``` в ядре «Linux» - временные записи, которые могут быть удалены при перезагрузке хоста.

Проверим запуск приложения на ARM-архитектуре:
```bash
$ docker run --rm --platform linux/arm64 aeshell/my-app:latest cat /arch
aarch64
```
