Код файла воркфлоу «ci.yml»:
```
name: ci

on:
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: m08/t04-docker-build-and-push
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
```

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

Тесты теперь будут запускаться на этапе «Pull Reques» (CI)» в ветку «main» - событие ```pull_request```, а сборка образа – только после слияния «Pull Reques» с «main» (CD) – событие ```push```.<br>
Из джобы ```build-push``` убрали зависимость ```needs: test```, так как в «main» попадает только код, успешно прошедший тесты.
