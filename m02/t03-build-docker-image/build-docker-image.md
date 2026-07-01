Соберем образ:
```bash
docker build -t my-app:1.0 .
```
```-t``` – имя образа.<br>
```.``` – путь к каталогу, в котором находится «dockerfile».

Проверим наличие образа:
```bash
$ docker images
                                                                                          i Info →   U  In Use
IMAGE           ID             DISK USAGE   CONTENT SIZE   EXTRA
my-app:1.0      02d1c58e3964        201MB         48.9MB    U
```
