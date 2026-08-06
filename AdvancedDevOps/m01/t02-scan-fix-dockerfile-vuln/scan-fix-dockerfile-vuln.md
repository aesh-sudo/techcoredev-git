Инструкцию по способам установки ```trivy``` можно посмотреть на официальной странице ```trivy``` в «GitHub».<br>
Проверка установки:
```bash
$ trivy --version
Version: 0.73.0
```

dockerfile:
```
FROM python:3.8-slim-buster
CMD ["python", "--version"]
```

dockerfile2:
```
FROM python:3.11-slim-bullseye
CMD ["python", "--version"]
```

Соберем образы:
```bash
$ docker build . -t my-app:v1.0
$ docker build . -f dockerfile2 -t my-app:v2.0
```

Команда проверки:
```
trivy image [options] имя_образа
```

```--severity HIGH,CRITICAL``` – параметр для вывода только важных и критических ошибок.

Справочная информация по командам ```trivy```:
```bash
trivy --help
```
