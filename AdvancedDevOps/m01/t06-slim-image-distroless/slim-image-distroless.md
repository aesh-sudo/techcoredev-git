```Distroless``` - это Docker-образы от «Google», которые содержат только приложение и его необходимые зависимости.<br>
Преимущества:
* Безопасность – чем меньше кода, тем безопаснее.
* Размер – минимальный размер образа.
* Скорость – быстрое скачивание и запуск.

Создадим go-приложение – файл «main.go»:
```go
package main

import (
    "fmt"
    "runtime"
)

func main() {
    fmt.Printf("Hello from %s/%s!\n", runtime.GOOS, runtime.GOARCH)
    fmt.Println("I'm running in a distroless container!")
}
```

Создадим «dockerfile» без «multi-stage», чтобы можно было проверить преимущества «multi-stage» и «distroless» - файл «dockerfile_bad»:
```
FROM golang:1.21-alpine
WORKDIR /app
COPY main.go .
RUN go build -o myapp main.go
CMD ["./myapp"]
```

Создадим «dockerfile» с использованием «multi-stage» и «distroless» - файл «dockerfile_good»:
```
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY main.go .
RUN go build -o myapp main.go

FROM gcr.io/distroless/static
COPY --from=builder /app/myapp /myapp

ENTRYPOINT ["/myapp"]
```

```gcr.io/distroless/static``` – урезанный образ на основе «Debian». Содержит все необходимое для запуска статически скомпилированного приложения.

Соберем образы и сравним их размеры:
```bash
$ docker build -f dockerfile_bad -t my-app-bad .
$ docker build -f dockerfile_good -t my-app-good .
$ docker images | grep my-app
my-app-bad:latest             3a3e7d124f4e      373MB       78MB
my-app-good:latest            c783fdc74314     9.33MB     1.94MB
```

Попытаемся войти в контейнеры:
```bash
$ docker run --rm -it my-app-bad /bin/sh
/app #
$ docker run --rm -it my-app-good /bin/sh
Hello from linux/amd64!
I'm running in a distroless container!
```

В контейнер, созданный на основе усеченного образа, войти нельзя, так как нет командной оболочки.
