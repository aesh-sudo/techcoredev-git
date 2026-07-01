```bash
$ docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS     NAMES
6960c26cb1b1   nginx     "/docker-entrypoint.…"   14 minutes ago   Up 14 minutes   80/tcp    bold_einstein

$ docker ps -a
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                      PORTS     NAMES
6960c26cb1b1   nginx         "/docker-entrypoint.…"   14 minutes ago   Up 14 minutes               80/tcp    bold_einstein
bd1b5ed69761   ubuntu        "bash"                   36 minutes ago   Exited (0) 35 minutes ago             sleepy_ptolemy
35fbc1c90d25   hello-world   "/hello"                 41 minutes ago   Exited (0) 41 minutes ago             busy_curran
```
