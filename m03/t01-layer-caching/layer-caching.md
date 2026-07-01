```bash
$ docker build -t my-app:1.0 .
...
=> [2/5] WORKDIR /app                                                                                                   0.7s
=> [3/5] COPY requirements.txt .                                                                                        0.1s
=> [4/5] COPY app.py .                                                                                                  0.1s
=> [5/5] RUN pip install --no-cache-dir -r requirements.txt                                                             5.9s
...

$ docker build -t my-app:1.0 .
...
=> CACHED [2/5] WORKDIR /app                                                                                            0.0s
=> CACHED [3/5] COPY requirements.txt .                                                                                 0.0s
=> CACHED [4/5] COPY app.py .                                                                                           0.0s
=> CACHED [5/5] RUN pip install --no-cache-dir -r requirements.txt                                                      0.0s
...
```
