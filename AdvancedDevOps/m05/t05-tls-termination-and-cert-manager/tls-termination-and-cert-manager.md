TLS-терминация – расшифровка HTTPS-трафика на входе в кластер. Преимущества:
* Один сертификат на ```Ingress```, а не на каждом Сервисе отдельно.
* Внутри кластера трафик идет по ```HTTP``` - быстрее и проще дебажить.
* Сертификаты обновляются в одном месте.

Для примера используем самоподписанный сертификат:
```bash
$ openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout my-tls.key \
  -out my-tls.crt \
  -subj "/CN=my-app.local" \
  -addext "subjectAltName=DNS:my-app.local,DNS:books.my-app.local,DNS:users.my-app.local"
```

```x509``` – стандарт сертификата.<br>
```nodes``` – отсутствие пароля на приватном ключе.<br>
```keyout``` – имя и место файла для сохранения приватного ключа.<br>
```out``` - имя и место файла для сохранения публичного сертификата.<br>
```subj``` – информация о владельце сертификата.<br>
```CN``` – общее имя. Чаще всего это доменное имя сайта или имя хоста.<br>
```addext``` – параметр позволяет добавить в сертификат расширение ```SAN``` - список альтернативных имен субъекта, для которых сертификат действителен. Современные клиенты (браузеры, почтовые клиенты) сверяют имя хоста с записями в ```SAN```.<br>
```DNS``` – идентификатор доменных имен в ```SAN```.

Проверим файлы сертификата:
```bash
$ ls -l my-tls.*
-rw-rw-r-- 1 aesh aesh 1212 Sep 16 11:42 my-tls.crt
-rw------- 1 aesh aesh 1704 Sep 16 11:42 my-tls.key
```

Поместим файлы сертификата в ```k8s``` как ```Secret```:
```bash
$ kubectl create secret tls my-tls \
  --cert=my-tls.crt \
  --key=my-tls.key
secret/my-tls created
```

Проверим наличие Секрета:
```bash
$ kubectl get secret my-tls
NAME     TYPE                DATA   AGE
my-tls   kubernetes.io/tls   2      30s
```

Создадим ```Ingress``` с блоком ```tls``` - файл ```tls-ingress.yml```:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - books.my-app.local
        - users.my-app.local
      secretName: my-tls
  rules:
    - host: books.my-app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: book-service
                port:
                  number: 80
    - host: users.my-app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: user-service
                port:
                  number: 80
```

```tls.hosts``` – список доменов, для которых действует сертификат.<br>
```tls.secretName``` – имя Секрета ```k8s```, в котором хранятся файлы сертификата.<br>
```ssl-redirect: "true"``` – аннотация. Автоматический редирект ```HTTP - HTTPS```.

Применим ```Ingress``` и проверим наличие:
```bash
$ kubectl apply -f tls-ingress.yml
ingress.networking.k8s.io/tls-ingress created

$ kubectl get ingress
NAME           CLASS   HOSTS                                   ADDRESS   PORTS     AGE
tls-ingress    nginx   books.my-app.local,users.my-app.local             80, 443   29s
```

```PORTS: 80, 443``` – ```Ingress``` слушает ```HTTP``` и ```HTTPS```.

Проверим приложения:
```bash
$ curl -k https://books.my-app.local/
book-service response
$ curl -k https://users.my-app.local/
user-service response
```

```-k (--insecure)``` – запрет проверки сертификата.

##########

```Cert-Manager``` – это k8s-оператор, который:
* Автоматически запрашивает сертификаты у ```CA``` (```Certificate Authority```).
* Сохраняет их в ```Secret```.
* Автоматически обновляет.
* Работает через аннотации в ```Ingress``` - ничего вручную генерировать не надо.

```Let's Encrypt``` - бесплатный ```CA```, который выдает сертификаты по протоколу ```ACME``` (```Automated Certificate Management Environment```). Используется способ подтверждения владения доменом ```HTTP-01 challenge```: ```Cert-Manager``` создает специальный файл на сервере (с токеном, который запрашивает у ```CA```), ```CA``` его запрашивает и подтверждает владение доменом.

Добавим репозиторий ```Jetstack``` и установим ```Cert-Manager```:
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

$ helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true
NAME: cert-manager
LAST DEPLOYED: Thu Sep 17 18:04:00 2026
NAMESPACE: cert-manager
STATUS: deployed
REVISION: 1
DESCRIPTION: Install complete
TEST SUITE: None
NOTES:
cert-manager v1.21.2 has been deployed successfully!

In order to begin issuing certificates, you will need to set up a ClusterIssuer
or Issuer resource (for example, by creating a 'letsencrypt-staging' issuer).

More information on the different types of issuers and how to configure them
can be found in our documentation:

https://cert-manager.io/docs/configuration/

For information on how to configure cert-manager to automatically provision
Certificates for Ingress resources, take a look at the `ingress-shim`
documentation:

https://cert-manager.io/docs/usage/ingress/

For information on how to configure cert-manager to automatically provision
Certificates for Gateway API resources, take a look at the `gateway resource`
documentation:

https://cert-manager.io/docs/usage/gateway/
```

В отдельное пространство имен устанавливается для изоляции компонентов управления сертификатами от рабочих нагрузок приложений.

```CRDs (Custom Resource Definitions)``` - разрешение для добавления пользовательских типов ресурсов (например, ```Certificate```, ```Issuer```, ```ClusterIssuer```).

Проверим созданные Поды:
```bash
$ kubectl get pods -n cert-manager
NAME                                      READY   STATUS    RESTARTS   AGE
cert-manager-5c4b7b5c7b-qvrwp             1/1     Running   0          174m
cert-manager-cainjector-c8785f548-k5q29   1/1     Running   0          174m
cert-manager-webhook-68877cb8f5-5msch     1/1     Running   0          174m
```

Также можно проверить статус приложения в ```helm```:
```bash
$ helm list -n cert-manager
NAME            NAMESPACE       REVISION        UPDATED                                 STATUS
   CHART                   APP VERSION
cert-manager    cert-manager    1               2026-09-17 18:04:00.341649875 +0000 UTC deployed
   cert-manager-v1.21.2    v1.21.2
```

Создадим ```ClusterIssuer``` для ```Let's Encrypt```:<br>
```Issuer``` – источник получения сертификатов (на уровне ```namespace```).<br>
```ClusterIssuer``` - источник получения сертификатов (на уровне кластера, доступен из любого ```namespace```).

Окружения ```Let's Encrypt```:<br>
```Staging``` – тестовый сервер. Лимиты выше, сертификаты не доверены браузерами.<br>
```Production``` – боевой сервер. Сертификаты доверены, но лимиты строже.

Создадим манифест ```ClusterIssuer``` - файл ```cluster-issuer-staging.yml```:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: aesh84@gmail.com
    privateKeySecretRef:
      name: letsencrypt-staging-key
    solvers:
      - http01:
          ingress:
            class: nginx
```

```server``` - ```URL``` ACME-сервера ```Let's Encrypt``` (```staging```).<br>
```email``` – почтовый адрес для получения уведомлений.<br>
```privateKeySecretRef``` - имя ```Secret```, в который будет сохранен приватный ключ ACME-аккаунта.<br>
```solvers.http01.ingress.class``` - используем ```HTTP-01 challenge``` через ```NGINX Ingress Controller```.

Применим и проверим ```ClusterIssuer```:
```bash
$ kubectl apply -f cluster-issuer-staging.yml
clusterissuer.cert-manager.io/letsencrypt-staging created

$ kubectl get clusterissuer
NAME                  READY   AGE
letsencrypt-staging   True    8s
```

Возьмем файл ```tls-ingress.yml``` из предыдущей задачи и добавим аннотации для ```Cert-Manager``` - файл ```cert-manager-ingress.yml```:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cert-manager-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-staging"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - books.my-app.local
        - users.my-app.local
      secretName: letsencrypt-tls
  rules:
    - host: books.my-app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: book-service
                port:
                  number: 80
    - host: users.my-app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: user-service
                port:
                  number: 80
```

```cert-manager.io/cluster-issuer: "letsencrypt-staging"``` – указание ```Cert-Manager```, какой ```ClusterIssuer``` использовать для получения сертификата.<br>
```secretName: letsencrypt-tls``` – ```Cert-Manager``` автоматически создаст этот ```Secret``` и положит туда сертификат.

Применим ```Ingress```:
```bash
$ kubectl apply -f cert-manager-ingress.yml
ingress.networking.k8s.io/cert-manager-ingress created
```

```Cert-Manager``` создал объект ```Certificate```. Проверим:
```bash
$ kubectl get certificate
NAME              READY   SECRET            AGE
letsencrypt-tls   False   letsencrypt-tls   36s
```

```READY: False``` - сертификат еще не получен. Проверим детали (особенно секцию ```Events```):
```bash
kubectl describe certificate letsencrypt-tls
```

```Cert-Manager``` создал ```CertificateRequest``` (запрос к ```Let's Encrypt```):
```bash
$ kubectl get certificaterequest
NAME                APPROVED   DENIED   READY   ISSUER
   REQUESTER                                         AGE
letsencrypt-tls-1   True                False   letsencrypt-staging
   system:serviceaccount:cert-manager:cert-manager   11m
```

```Cert-Manager``` не создал ```Order``` (```ACME-order```):
```bash
$ kubectl get order
NAME                           STATE     AGE
letsencrypt-tls-1-2958535336   errored   18m
```

Проверим параметры ```Order```:
```bash
kubectl describe order letsencrypt-tls-1-2958535336
```

Ошибка произошла из-за того, что домен ```local``` не является ```Valid public suffix``` (```TLD```) – публичное расширение (суффикс) домена.

Порядок проверки в ACME-протоколе (```Let's Encrypt```):
1. Валидация идентификатора (имя домена) - Проверка ```TLD``` в ```Public Suffix List```.
2. DNS-резолвинг – резолвится ли домен в IP-адрес.
3. ```ACME challenge``` (```HTTP-01 / DNS-01```) – доказательство владения доменом.
4. Подпись сертификата.

То есть, мы споткнулись уже на первом шаге.
