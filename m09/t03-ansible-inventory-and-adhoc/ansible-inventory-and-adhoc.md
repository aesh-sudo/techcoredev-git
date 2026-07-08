### Задача (Inventory): Создать inventory.ini. ###

Создадим файл ```inventory.ini```:
```
[local]
localhost ansible_connection=local
```

```[local]``` – имя группы хостов для массового управления ими.<br>
```localhost``` – имя хоста. Будет участвовать в отчетах и логах «Ansible».<br>
```ansible_connection=local``` – переменная (настройка), которая передается хосту. Указывает «Ansible», какой механизм использовать для связи с сервером.<br>
По умолчанию «Ansible» выполняет подключение к хосту по «SSH». Значение «local» указывает «Ansible», что команды надо выполнять напрямую на текущей машине, используя локальный интерпретатор «Python».

### Задача (Ad-Hoc - ping): Проверить связь: ansible local -i inventory.ini -m ping. ###
```bash
$ ansible local -i inventory.ini -m ping
localhost | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3.12"
    },
    "changed": false,
    "ping": "pong"
}
```

Команда:<br>
```local``` – имя группы хостов из инвентаря, к которой мы обращаемся.<br>
```-i``` – параметр для указания пути к файлу инвентаря.<br>
```-m``` – параметр для указания вызываемого модуля.<br>
```ping``` – модуль «Ansible», проверяющий успешность подключения, установленный «Python» и возможность выполнения модуля на целевом хосте.

Результат:<br>
```SUCCESS``` – модуль отработал успешно.<br>
```"ping": "pong"``` – целевой хост отвечает и готов к работе.<br>
```"changed": false``` – модуль ничего не поменял в целевой системе.<br>
```"discovered_interpreter_python": "/usr/bin/python3.12"``` – интерпретатор «Python», использованный на целевой машине для выполнения модуля.

### Задача (Ad-Hoc - setup): Собрать "факты" о машине: ansible local -i inventory.ini -m setup. ###
```bash
$ ansible local -i inventory.ini -m setup
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_all_ipv4_addresses": [
            "172.18.0.1",
            "192.168.1.92",
            "172.17.0.1"
        ],
...
        "ansible_virtualization_tech_host": [],
        "ansible_virtualization_type": "virtualbox",
        "discovered_interpreter_python": "/usr/bin/python3.12",
        "gather_subset": [
            "all"
        ],
        "module_setup": true
    },
    "changed": false
}
```

```setup``` - модуль «Ansible», собирающий информацию о целевом хосте.

Информацию можно отфильтровать. Например:
```bash
$ ansible local -i inventory.ini -m setup -a "filter=ansible_mem*"
localhost | SUCCESS => {
    "ansible_facts": {
        "ansible_memfree_mb": 2502,
        "ansible_memory_mb": {
            "nocache": {
                "free": 3513,
                "used": 402
            },
            "real": {
                "free": 2502,
                "total": 3915,
                "used": 1413
            },
            "swap": {
                "cached": 0,
                "free": 2044,
                "total": 2044,
                "used": 0
            }
        },
        "ansible_memtotal_mb": 3915,
        "discovered_interpreter_python": "/usr/bin/python3.12"
    },
    "changed": false
}
```

```-a``` – параметр для передачи значений специфических аргументов модуля.

Узнать информацию о модуле, в том числе о его специфических аргументах:
```bash
ansible-doc имя_модуля
```

Пример:
```bash
$ ansible-doc setup
...

   filter  If supplied, only return facts that match one of the shell-style (fnmatch) pattern. An empty list basically means 'no filter'. As of Ansible 2.11,
           the type has changed from string to list and the default has became an empty list. A simple string is still accepted and works as a single pattern.
           The behaviour prior to Ansible 2.11 remains.
        default: []
        elements: str
        type: list
...
```

### Задача (Ad-Hoc - apt): Установить Nginx: ansible local -i inventory.ini -m apt -a "name=nginx state=present" --become. ###
```bash
$ ansible local -i inventory.ini -m apt -a "name=nginx state=present" --become -K
BECOME password:
localhost | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3.12"
    },
    "cache_update_time": 1783502613,
    "cache_updated": false,
    "changed": true,
...
}
```
Команда:<br>
```state=present``` – аргумент модуля ```apt```. Состояние: установить (если не установлен).<br>
```--become``` - выполнить команду с правами ```root``` (через ```sudo```).<br>
```-K (--ask-become-pass)``` – запросить пароль для выполнения команды с правами ```root```.

Результат:<br>
```CHANGED``` – «Ansible» внес изменения в систему.<br>
```"changed": true``` – требуемый пакет был установлен.

### Задача (Идемпотентность): Запустить команду из Задачи 6 еще раз. ###

Результат при повторном запуске:
```bash
$ ansible local -i inventory.ini -m apt -a "name=nginx state=present" --become -K
BECOME password:
localhost | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3.12"
    },
    "cache_update_time": 1783502613,
    "cache_updated": false,
    "changed": false
}
```

```"changed": false``` – пакет уже установлен, «Ansible» ничего не менял.

### Задача (Ad-Hoc - service): Убедиться, что сервис запущен: ansible local -i inventory.ini -m service -a "name=nginx state=started enabled=yes" --become. ###

Проверить установку приложения можно:<br>
Напрямую:<br>
```systemctl status nginx``` – полная информация о состоянии приложения.<br>
```systemctl is-active nginx``` – только статус приложения. Часто используется в скриптах.<br>
```systemctl is-enabled``` – состояние автозагрузки приложения.

Через «Ansible»:<br>
Полная информация о состоянии приложения:
```bash
ansible local -i inventory.ini -m command -a "systemctl status nginx"
```
Только статус приложения:
```bash
ansible local -i inventory.ini -m command -a "systemctl is-active nginx"
```
Состояние автозагрузки приложения:
```bash
ansible local -i inventory.ini -m command -a "systemctl is-enabled nginx"
```

```bash
$ ansible local -i inventory.ini -m service -a "name=nginx state=started enabled=yes"
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3.12"
    },
    "changed": false,
    "enabled": true,
    "name": "nginx",
    "state": "started",
    "status": {
	...
    }
}
```

```service``` – модуль управления службами.<br>
```state=started``` – аргумент модуля. Если служба остановлена, то будет запущена. Если служба запущена, то ничего не произойдет (идемпотентность).<br>
```enabled=yes``` - аргумент модуля. Если службы нет в автозагрузке, то будет добавлена. Если служба уже в автозагрузке, то ничего не произойдет (идемпотентность).

### Задача (Ad-Hoc - file): Создать папку: ansible local -i inventory.ini -m file -a "path=/tmp/test-ansible state=directory". ###
```bash
$ ansible local -i inventory.ini -m file -a
"path=~/techcoredev-git/m09/t03-ansible-inventory-and-adhoc/tmp/test-ansible state=directory"
localhost | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3.12"
    },
    "changed": true,
    "gid": 1000,
    "group": "aesh",
    "mode": "0775",
    "owner": "aesh",
    "path": "/home/aesh/techcoredev-git/m09/t03-ansible-inventory-and-adhoc/tmp/test-ansible",
    "size": 4096,
    "state": "directory",
    "uid": 1000
}
```

```file``` – модуль управления файлами и каталогами.<br>
```path``` – аргумент модуля, который задает путь к каталогу.<br>
```state``` - аргумент модуля, который задает тип создаваемого элемента – каталог.

### Задача (Ad-Hoc - copy): Скопировать файл: ansible local -i inventory.ini -m copy -a "src=inventory.ini dest=/tmp/test-ansible/inventory.bak". ###
```bash
$ ansible local -i inventory.ini -m copy -a "src=inventory.ini dest=./tmp/test-ansible/inventory.bak"
localhost | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3.12"
    },
    "changed": true,
    "checksum": "fa8b1e0836b45ec681b11ba7b50d9171d2cc8296",
    "dest": "./tmp/test-ansible/inventory.bak",
    "gid": 1000,
    "group": "aesh",
    "md5sum": "a4941d74e48dc9851b1916b345fc4d69",
    "mode": "0664",
    "owner": "aesh",
    "size": 43,
    "src": "/home/aesh/.ansible/tmp/ansible-tmp-1783534406.2352326-7881-262717611895655/.source.bak",
    "state": "file",
    "uid": 1000
}
```

```copy``` – модуль копирования заданных элементов.<br>
```src``` – если в конце пути стоит слеш (```/```), то будет скопировано содержимое указанного каталога. Если слеша нет, то будет скопирован каталог со всем его содержимым.
