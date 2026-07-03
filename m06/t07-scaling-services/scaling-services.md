```bash
$ docker compose up -d --scale app=3
[+] up 4/5
 ✔ Container module6_3-redis-1 Healthy                                                                                        7.0s
 ✔ Container module6_3-db-1    Healthy                                                                                         7.0s
 ✔ Container module6_3-app-3   Created                                                                                         0.3s
 ✔ Container module6_3-app-1   Started                                                                                         7.1s
 ⠴ Container module6_3-app-2   Starting                                                                                         8.5s
Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint module6_3-app-2 (f7a87692c0eebc2d3e1a28b994aa80e4c0bbf6da05a312259ba87875c9dd6977): Bind for 0.0.0.0:5000 failed: port is already allocated

$ docker compose ps
NAME                IMAGE           COMMAND                  SERVICE   CREATED
          STATUS                    PORTS
module6_3-app-1     module6_3-app   "gunicorn --bind 0.0…"   app       26 seconds ago
          Up 19 seconds             0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
module6_3-db-1      postgres        "docker-entrypoint.s…"   db        26 seconds ago
          Up 25 seconds (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
module6_3-redis-1   redis           "docker-entrypoint.s…"   redis     26 seconds ago
          Up 25 seconds (healthy)   0.0.0.0:6379->6379/tcp, [::]:6379->6379/tcp
```

```--scale``` – параметр для запуска нескольких одинаковых экземпляров (контейнеров) указанного сервиса.

Нюансы:<br>
Конфликт портов – если для масштабируемого сервиса жестко прописаны порты, то команда выдаст ошибку. Три контейнера не могут одновременно занимать один порт.<br>
Решение: убрать привязку к портам или вынести балансировку в отдельный контейнер, который будет проксировать запросы к контейнерам.

Имена контейнеров – в «docker-compose.yml» нельзя использовать параметр ```container_name```. Имена контейнеров должны быть уникальными.

Контейнеры окажутся в одной docker-сети. Если другой контейнер в этой же сети обратится к ним по имени сервиса, то встроенный «DNS Docker Compose» автоматически будет балансировать нагрузку между инстансами.
