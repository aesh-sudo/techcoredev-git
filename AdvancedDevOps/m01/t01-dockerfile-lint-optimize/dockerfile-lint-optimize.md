Линтер – инструмент для анализа исходного кода программы на соответствие определенным правилам.<br>
```hadolint``` – линтер для «dockerfile».

Инструкцию по способам установки ```hadolint``` можно посмотреть на официальной странице ```hadolint``` в «GitHub».<br>
Проверка установки:
```bash
$ hadolint --version
Haskell Dockerfile Linter 2.15.1
```

Создадим некорректный «dockerfile»:
```
FROM ubuntu:22.04
RUN apt update
RUN apt install -y curl
```

Проанализируем код «dockerfile»:
```bash
$ hadolint dockerfile
...
dockerfile:2 DL3009 info: Delete the apt lists (/var/lib/apt/lists) after installing something
...
```

```dockerfile:2``` – имя файла и номер строки.<br>
```DL3009``` – код правила.<br>
```info/warning/error``` - уровень важности.

Исправленный «dockerfile»:
```
FROM ubuntu:22.04
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl=8.21.0 \
  && rm -rf /var/lib/apt/lists/*
```

Справочная информация по командам ```hadolint```:
```bash
hadolint --help
```
