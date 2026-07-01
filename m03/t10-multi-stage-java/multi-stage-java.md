Создадим файл с кодом приложения на «Java» - «App.java»:
```java
package com.example;

public class App {
    public static void main(String[] args) {
        System.out.println("Hello, World from Docker!");
        System.out.println("Java version: " + System.getProperty("java.version"));
    }
}
```

Создадим «dockerfile_java»:
```
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app
COPY App.java ./src/com/example/App.java                      1

RUN mkdir -p ./build/classes                                  2
RUN javac -d ./build/classes ./src/com/example/App.java       3
RUN jar cf ./build/app.jar -C ./build/classes .               4

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/build/app.jar ./app.jar

ENTRYPOINT ["java", "-cp", "app.jar", "com.example.App"]      5
```

```1``` – структура каталогов создается по имени пакета. Имя пакета:
```
com.example
```
Значит структура каталогов, куда помещается файл с кодом, должна быть:
```
./src/com/example/
```

```2, 3``` – создаем каталог, куда будут помещены скомпилированные классы, и компилируем их.<br>
```-d``` – параметр для указания пути, куда будут положены скомпилированные классы.

```4``` – создание jar-архива.<br>
```c (create)``` – параметр для создания нового jar-архива.<br>
```f``` – имя создаваемого jar-архива.<br>
```-C``` – сменить директорию перед добавлением файлов в jar-архив.<br>
```.``` – добавить в jar-архив все файлы из текущего каталога (который сменили в предыдущем параметре).

```5``` – запуск приложения с явным указанием главного класса, так как не использовали файл ```MANIFEST.MF```, в котором указывается главный класс.

Соберем образ:
```
docker build -f dockerfile_java -t java-app .
```
Проверим размер образа:
```
$ docker images
                                                                                          i Info →   U  In Use
IMAGE                       ID             DISK USAGE   CONTENT SIZE   EXTRA
java-app:latest             0027aab48567        256MB         67.9MB
```
Запустим контейнер:
```
$ docker run --rm java-app
Hello, World from Docker!
Java version: 17.0.19
```
