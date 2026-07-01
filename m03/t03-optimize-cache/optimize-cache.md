Так как код приложения во время разработки и эксплуатации может меняться, то слой с копированием файла приложения поместим ниже слоев с копированием файла зависимостей и их установкой.<br>
Создадим образ:
```bash
$ docker build -t my-app:1.0 .
...
=> [2/5] WORKDIR /app                                                                                                   0.7s
=> [3/5] COPY requirements.txt .                                                                                        0.1s
=> [4/5] RUN pip install --no-cache-dir -r requirements.txt                                                             6.4s
=> [5/5] COPY app.py .                                                                                                  0.2s
...
```
Повторно соберем образ:
```bash
$ docker build -t my-app:1.0 .
...
=> CACHED [2/5] WORKDIR /app                                                                                            0.0s
=> CACHED [3/5] COPY requirements.txt .                                                                                 0.0s
=> CACHED [4/5] RUN pip install --no-cache-dir -r requirements.txt                                                      0.0s
=> CACHED [5/5] COPY app.py .                                                                                           0.0s
...
```
Изменим код приложения в файле «app.py» и снова пересоберем образ:
```bash
$ docker build -t my-app:1.0 .
...
=> CACHED [2/5] WORKDIR /app                                                                                            0.0s
=> CACHED [3/5] COPY requirements.txt .                                                                                 0.0s
=> CACHED [4/5] RUN pip install --no-cache-dir -r requirements.txt                                                      0.0s
=> [5/5] COPY app.py .                                                                                                  0.1s
...
```
Видим, что теперь слои с копированием файла зависимостей и их установкой кешируются, а не собираются заново, что ускоряет время сборки образа.
