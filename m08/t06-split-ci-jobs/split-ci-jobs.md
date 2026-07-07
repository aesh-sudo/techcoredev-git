Код файла воркфлоу «ci.yml»:
```
name: ci
on:
  pull_request:
    branches:
      - main
    path:
      - 'm08/t04-docker-build-and-push/**'
      - '!m08/t04-docker-build-and-push/*.md'
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: m08/t04-docker-build-and-push        1
    steps:
      - name: checkout
        uses: actions/checkout@v7

      - name: setup
        uses: actions/setup-python@v6
        with:
          python-version: '3.10'

      - name: run
        run: |
          pip install -r tests/requirements.txt
          PYTHONPATH=src pytest tests/

  build-push:
    needs: test                                                 2
    run-on: ubuntu-latest
    steps:
      - name: checkout                                          3
        uses: actions/checkout@v7

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
          push: true
          tags: |
            ghcr.io/aesh-sudo/m08-t04-docker-build-and-push:latest
            ghcr.io/aesh-sudo/m08-t04-docker-build-and-push:${{ github.sha }}
```

```1``` – ```defaults.run.working-directory``` только в ```test```, так как в этой директории находится каталог с тестами и, соответственно, зависимости тоже должны быть установлены в этой директории.<br>
В ```build-push``` пути указаны явно в ```context``` и ```file```, поэтому ```working-directory``` не нужен.

```2``` – если ```test``` завершился с ошибкой, то ```build-push``` не запустится (статус «skipped»). Если ```test``` отменен, то ```build-push``` тоже будет отменен.<br>

```3``` – каждый джоб запускается на новой виртуальной машине, поэтому необходимо скопировать файлы проекта.

Специально оставил код:
```
    path:
      - 'm08/t04-docker-build-and-push/**'
      - '!m08/t04-docker-build-and-push/*.md'
```

Работали в ветке ```m08-t06-split-ci-jobs```, но пайплайн все равно запустился, так как при изменении файла воркфлоу «ci.yml» пайплайн выполняется всегда.
ТЕСТ
