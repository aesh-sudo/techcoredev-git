Файл шаблона конфигурации ```nginx.conf.j2```:
```
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    access_log /var/log/nginx/access.log;
    error_log  /var/log/nginx/error.log;

    server {
        listen {{ nginx_port }};
        server_name localhost;

        root /var/www/html;
        index index.nginx-debian.html index.html index.htm;

        location / {
            try_files $uri $uri/ =404;
        }
    }
}
```

```listen {{ nginx_port }}``` – место в шаблоне, куда будет вставлено значение переменной ```nginx_port```, заданной в сценарии.

Файл «inventory.ini»:
```
[local]
localhost ansible_connection=local
```

Файл «nginx-playbook.yml»:
```
- hosts: local
  become: true

  vars:
    nginx_port: 80

  tasks:
    - name: Update apt cache                  1
      apt:
        update_cache: yes

    - name: Install Nginx                     2
      apt:
        name: nginx
        state: present

    - name: Start Nginx                       3
      service:
        name: nginx
        state: started
        enabled: yes

    - name: Deploy nginx.conf from template
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart Nginx

  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
```

```hosts: local``` – имя хоста в файле «inventory.ini», на котором будет выполняться сценарий.<br>
```become: true``` - запуск задач с правами ```root``` (```sudo```).<br>
```vars:``` - определение переменной ```nginx_port: 80```. Будет доступна во всем сценарии.

```1``` - обновление кеша ```apt``` перед установкой пакетов.<br>
```2``` – установка пакета «nginx».<br>
```3``` – запуск сервиса и добавление его в автозагрузку.

```template:``` - в указанный файл шаблона вставляются значения переменных, указанных, в данном случае, в сценарии, и файл копируется в указанное место на хосте.<br>
```notify:``` - вызов обработчика (```handlers```). Обработчик выполняется только если задача внесла изменения.<br>
```handlers:``` - обработчик. Обработчики выполняются в конце работы сценария. Если обработчик в рамках одного сценария указывается несколько раз, то выполнится он все равно только один раз.

Запустим сценарий:
```bash
ansible-playbook -i inventory.ini nginx-playbook.yml -K
```
