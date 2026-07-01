```
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
COPY app.py .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```
```--no-cache-dir``` – отключает кеширование загруженных пакетов. В образ попадут только установленные библиотеки, а не временные файлы.<br>
```-r``` – параметр для указания файла, из которого необходимо прочитать список зависимостей для установки.
