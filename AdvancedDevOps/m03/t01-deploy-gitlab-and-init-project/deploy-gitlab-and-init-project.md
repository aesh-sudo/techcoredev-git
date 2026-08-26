Для установки «GitLab» в домашнем каталоге создадим каталог ```gitlab-install```, а в нем файл «docker-compose.yml»:
```
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    container_name: gitlab
    restart: always
    hostname: 'gitlab.aesh.com'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://gitlab.aesh.com:8929'
        gitlab_rails['gitlab_shell_ssh_port'] = 10022
    ports:
      - '8929:8929'
      - '10022:22'
    volumes:
      - 'gitlab_config:/etc/gitlab'
      - 'gitlab_logs:/var/log/gitlab'
      - 'gitlab_data:/var/opt/gitlab'
    shm_size: '256m'
volumes:
  gitlab_config:
  gitlab_logs:
  gitlab_data:
```

Примерно такой файл «docker-compose.yml» описан в разделе установки на официальном сайте «GitLab».<br>
```GITLAB_OMNIBUS_CONFIG``` – переменная окружения, в которую можно передать код (```Ruby```) для настройки конфигурации «GitLab». При старте контейнера запускается ```Omnibus``` - скрипт, который читает этот блок и настраивает сервисы «GitLab».

```external_url``` – внешний адрес «GitLab». Заданный порт является внутренним портом «Nginx», поэтому в блоке ```ports``` должны быть соответствующие порты – ```8929:8929```.

```gitlab_rails['gitlab_shell_ssh_port']``` – настройка внутреннего компонента «GitLab Shell», который обеспечивает работу «git clone», «git push» и «git pull» через «SSH». Внутри контейнера всегда слушает порт «22». Настройка задает внешний порт для подключения по «SSH».

После установки «GitLab» будет доступен по адресу:
```
http://gitlab.aesh.com:8929
```

Данные для первоначального входа в «GitLab»:<br>
Пользователь:
```
root
```
Пароль можно получить с помощью команды:
```
sudo docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

Файл с паролями автоматически удалится через сутки после первого запуска контейнера с «GitLab».

На хосте создадим каталог ```~/projects/my-app``` и создадим в нем файлы приложения:<br>
app.py:
```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
```

test_app.py:
```python
from app import add, subtract

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    assert subtract(-1, -1) == 0
```

requirements.txt:
```python
pytest==7.4.0
```

Инициализируем «Git» и выполним коммит:
```bash
git init
git branch -M main
git add .
git commit -m "feat: initial commit of my-app"
```

В «GitLab» создадим проект (пустой):
```
Create a project - Create blank project
```
Свойства:
```
Project name: my-app.
Project URL (namespace): root.
Initialize repository with a README: false.
```

После создания проекта откроется страница пустого проекта с подсказками ```Command line instructions``` - там будут готовые команды для «push».<br>
Привяжем «Git» с проектом к репозиторию в «GitLab»:
```bash
git remote add origin http://gitlab.aesh.com:8929/root/my-app.git
```

```remote``` – работаем с удаленным репозиторием.<br>
```add``` – добавим новый удаленный репозиторий.<br>
```origin``` – имя удаленного репозитория (задается произвольно).<br>
```http//...``` - «URL» удаленного репозитория.

Выполним «push» проекта в «GitLab»:
```bash
git push -u origin main
```
