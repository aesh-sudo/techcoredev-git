dockerfile_appuser:
```
FROM alpine:latest
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```
```-S``` – параметр для создания системной группы и системного пользователя. Обычно создаются для демонов. Не имеют домашней директории, пароля и «shell». Ограничены в правах.
```
USER appuser
```
Переключение контекста выполнения последующих команд и приложения на непривилегированного пользователя.

Проверка:
```bash
$ docker run --rm -it appuser sh
/ $ whoami
appuser
/ $ id
uid=100(appuser) gid=101(appgroup) groups=101(appgroup),101(appgroup)
```
