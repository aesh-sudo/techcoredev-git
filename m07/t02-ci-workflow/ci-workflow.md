```.github/workflows``` – каталог, который создается в корне каталога с «git», для хранения файлов воркфлоу (```.yml```) «GitHub Actions».

Создадим файл воркфлоу «ci.yml»:
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
      - name: setup
        uses: actions/setup-python@v6
        with:
          python-version: '3.10'
      - name: run
        run: |
          pip install -r requirements.txt
          pytest
```
```defaults:``` - глобальные настройки для всех шагов текущей джобы.<br>
```run: working-directory:``` - указание рабочей директории для всех команд ```run:```. Все команды ```action``` (```uses```) при этом выполняются в корне. Выполнение ```run:``` необходимо в директории ```m07/t02-ci-workflow```, потому что в ней находятся файлы, участвующие в командах ```run:```.

В каталоге задачи ```m07/t02-ci-workflow``` создадим файлы, необходимые для ```pytest```.<br>
Для зависимостей создадим файл с именем ```requirements.txt``` и укажем в нем:
```
pytest
```
Создадим каталог «tests» для размещения файлов с тестами. «pytest» выполняет поиск файлов с тестами именно в каталоге с таким наименование. Файлы в каталоге:<br>
```__init__.py``` – файл для того, чтобы «Python» воспринимал каталог как «пакет» (```package```), в котором находятся модули.<br>
```test_dummy.py``` – файл с условной процедурой тестирования.

При вызове в «GitHub» процедуры «Pull request» выполняется воркфлоу (на закладке «Actions»).<br>
Если в «GitHub» уже есть открытый «Pull request» из ветки разработки в основную ветку, то воркфлоу сработает уже при ```git push```.
