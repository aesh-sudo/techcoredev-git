Так как мы сделали секреты в «GHCR», то будем использовать подключение к нему (```ghcr.io```).<br>
Изменим файл воркфлоу «ci.yml»:
```
name: ci
on:
  pull_request:
    branches:
      - main
    path:
      - 'm07/t02-ci-workflow/**'
      - '!m07/t02-ci-workflow/*.md'
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: m07/t02-ci-workflow
    steps:
      - name: checkout
        uses: actions/checkout@v7

      - name: Login to GHCR
        uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: setup
        uses: actions/setup-python@v6
        with:
          python-version: '3.10'

      - name: run
        run: |
          pip install -r requirements.txt
          pytest
```

Для аутентификации в хранилище будем использовать готовый action ```docker/login-action@v4```.<br>
Аутентификацию делают до шагов, в которых будет выполняться работа с хранилищем.
