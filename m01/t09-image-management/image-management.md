```bash
$ docker images
                                                                                          i Info →   U  In Use
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest   96498ffd522e       25.9kB         9.49kB    U
nginx:latest         42f2d24ae18d        241MB           66MB    U
ubuntu:latest        53958ec7b67c        160MB         45.3MB    U
```
Удалить образ можно только после удаления контейнеров, которые с ним связаны.
```bash
docker rmi image_name/image_id
```
