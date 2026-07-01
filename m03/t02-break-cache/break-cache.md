Изменим в файле приложения «app.py» код – добавим восклицательных знаков в строку:
```python
return '<h1>Hello, World!!! Я работаю внутри Docker-контейнера!!!</h1>'
```
Результат:
```bash
$ docker build -t my-app:1.0 .
...
=> CACHED [2/5] WORKDIR /app                                                                                              0.0s
=> CACHED [3/5] COPY requirements.txt .                                                                                   0.0s
=> [4/5] COPY app.py .                                                                                                    0.1s
=> [5/5] RUN pip install --no-cache-dir -r requirements.txt                                                               6.2s
...
```
Видим, что те этапы, которые кешировались, начиная с этапа «4/5» при сборке не кешировались, а пересобирались заново.
