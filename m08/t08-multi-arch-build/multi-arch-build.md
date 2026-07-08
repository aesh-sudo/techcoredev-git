```Buildx``` – расширенный CLI-плагин для «Docker», который предоставляет:
* Поддержку «multi-platform» сборок – сборка образов под разные архитектуры одновременно.
* Продвинутое кеширование.
* Параллельную сборку нескольких стадий.
* Возможность создавать несколько builder-инстансов с разными драйверами.

Без ```Buildx``` «Docker» может собирать образы только под архитектуру хоста (на «GH Actions» это «linux/amd64»).<br>
```QEMU``` – эмулятор процессора. Необходим для сборки образов с архитектурой, отличной от архитектуры хоста.

Порядок действий в воркфлоу:
* «QEMU» регистрирует эмуляторы для нужных архитектур.
* «Buildx» создает «builder», который видит архитектуры, предоставленные «QEMU».
* «build-push-action» собирает образ для каждой платформы и создает ```manifest list```.

```manifest list``` – специальный список, который указывает, какой образ необходимо тянуть (```pull```) для конкретной архитектуры.

Код файла воркфлоу «cd.yml»:
```
name: cd

on:
  push:
    branches:
      - main

jobs:
  build-push:
    runs-on: ubuntu-latest

    steps:
      - name: checkout
        uses: actions/checkout@v7

        # Установим QEMU - эмулятор для сборки под разные архитектуры
      - name: set up QEMU
        uses: docker/setup-qemu-action@v4
        with:
          platforms: linux/amd64,linux/arm64                                       1

        # Устанавливаем buildx - расширенный сборщик docker-образов
      - name: set up docker buildx
        uses: docker/setup-buildx-action@v4                                        2

      - name: login to GHCR
        uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: build and push
        uses: docker/build-push-action@v7
        with:
          context: ./m08/t04-docker-build-and-push
          file: ./m08/t04-docker-build-and-push/docker/dockerfile
          platforms: linux/amd64,linux/arm64                                       3
          push: true
          tags: |
            ghcr.io/aesh-sudo/m08-t04-docker-build-and-push:latest
            ghcr.io/aesh-sudo/m08-t04-docker-build-and-push:${{ github.sha }}
```

```1``` – указание необходимых архитектур. Если не указать, то установятся все доступные архитектуры.<br>
```2``` – установка создает builder-инстанс с драйвером «docker-container», который видит QEMU-эмуляторы из шага 1.<br>
```3``` – указание, для каких архитектур собирать образы. Формат:
```
os/arch[/variant]
```
