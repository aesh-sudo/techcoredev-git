Зайдем в контейнер, созданный в предыдущей задаче, создадим в «postgres» таблицу «users» и внесем в нее данные:
```bash
$ docker exec -it 24c1b3066638 psql -U postgres
postgres=# CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100), age INT);
CREATE TABLE
postgres=# INSERT INTO users (name, age) VALUES ('Алексей', 30), ('Мария', 25);
INSERT 0 2
postgres=# SELECT * FROM users;
 id |  name   | age
----+---------+-----
  1 | Алексей |  30
  2 | Мария   |  25
(2 rows)
```
Остановим и удалим контейнер и вновь создадим контейнер с теми же параметрами. Зайдем в него и проверим данные в БД:
```bash
$ docker exec -it d78cbbaaf3bf psql -U postgres
psql (18.4 (Debian 18.4-1.pgdg13+1))
Type "help" for help.

postgres=# SELECT * FROM users;
 id |  name   | age
----+---------+-----
  1 | Алексей |  30
  2 | Мария   |  25
(2 rows)
```
Вывод: именованный том не удаляется при удалении контейнера и к нему можно подключиться вновь.
