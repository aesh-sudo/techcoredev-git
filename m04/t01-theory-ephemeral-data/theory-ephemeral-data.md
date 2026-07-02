Создадим контейнер и зайдем в него. Создадим в нем файл, выйдем и удалим контейнер:
```bash
$ docker run -it ubuntu bash
root@4425e2d3d49d:/# touch test.txt
root@4425e2d3d49d:/# ls
bin boot dev etc home lib lib64 media mnt opt proc root run sbin srv sys test.txt tmp usr var
root@4425e2d3d49d:/#
exit
$ docker rm 4425e2d3d49d
4425e2d3d49d

$ docker run -it ubuntu bash
root@2e7357d98ce7:/# ls
bin boot dev etc home lib lib64 media mnt opt proc root run sbin srv sys tmp usr var
```
Вместе с уничтожением контейнера уничтожаются и все его данные.
