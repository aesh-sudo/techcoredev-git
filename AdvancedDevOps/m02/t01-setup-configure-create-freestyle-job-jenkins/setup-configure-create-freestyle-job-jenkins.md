```LTS (Long Term Support / Долгосрочная Поддержка)``` – стабильная версия «Jenkins».

Запустим «Jenkins» в «Docker»:
```bash
docker run -d -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home --name jenkins jen-kins/jenkins:lts
```

```8080``` – порт для веб-интерфейса (доступ к «UI Jenkins» через браузер).<br>
```50000``` – порт для агентов (```workers```).

Получим ```initialAdminPassword``` - указан в логах установки «Jenkins»:
```bash
docker logs jenkins
```

Также в логах указан путь к файлу, в котором находится ```initialAdminPassword```.

В браузере, на странице «Jenkins» необходимо указать полученный пароль.<br>
Далее установим необходимые для работы плагины, выбрав пункт ```Install suggested plugins```, и создадим учетную запись администратора.

Чтобы не возникало путаницы с переводом, можно задать язык по умолчанию:<br>
Откроем меню:
```
Manage Jenkins (Настройки) – Plugins - Available plugins
```
список плагинов, доступных для установки. Найдем плагин ```Locale``` и установим его.

Откроем меню:
```
Manage Jenkins – Apperance
```
настройки внешнего вида «Jenkins».<br>
Установим:
```
Default Language - Use Default Locale - English (en)
```
и поставим галочку:
```
Ignore browser preference and force this language to all users
(Игнорировать настройки браузера и принудительно использовать этот язык для всех пользователей).
```

Создание конфигурации:<br>
Выбираем ```Create a job``` - Вводим имя конфигурации ```hello-jenkins``` и выбираем ее тип ```Freestyle project```.<br>
Настройки конфигурации:<br>
```Source Code Management``` (управление исходным кодом) – выбираем пункт ```Git``` и заполняем поле:<br>
```Repository URL``` (адрес репозитория):
```
https://github.com/octocat/Hello-World
```

```Build Steps``` (шаги сборки) – добавляем новый шаг типа ```Execute shell```. В окне ```Command``` пишем команду:
```
echo "Hello Jenkins"
```

И сохраняем конфигурацию.

Запуск сборки:<br>
На странице сборки в левом меню необходимо выполнить команду ```Build Now```.

Просмотр логов сборки:<br>
Нажать на номер сборки (например, ```#1```) и выбрать пункт меню ```Console Output```.

Выполненные «Jenkins» действия:
* Клонирование заданного репозитория в каталог:
  ```
  /var/jenkins_home/workspace/hello-jenkins
  ```
* Выполнение команд из настройки ```Build Steps```.
* Запись вывода в логи.
