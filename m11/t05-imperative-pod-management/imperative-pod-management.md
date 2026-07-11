### Задача (Императивный запуск): Запустить Nginx без YAML: kubectl run my-nginx --image=nginx. ###
```bash
$ kubectl run my-nginx --image=nginx
pod/my-nginx created
```
```my-nginx``` – имя пода.<br>
```--image=nginx``` – образ, на основании которого будет создан контейнер внутри пода.

### Задача (Управление): kubectl get pods. kubectl describe pod my-nginx. ###

Посмотреть все поды в текущем пространстве имен:
```bash
$ kubectl get pods
NAME       READY   STATUS    RESTARTS   AGE
my-nginx   1/1     Running   0          3m56s
```

Если под еще не создался, то его статус будет таким:
```bash
$ kubectl get pods
NAME       READY   STATUS              RESTARTS   AGE
my-nginx   0/1     ContainerCreating   0          2s
```

Если в пространстве имен не создано ни одного пода, то будет выведено сообщение об этом:
```bash
$ kubectl get pods
No resources found in default namespace.
```

```resources``` – в терминах «k8s» под – это ресурс.

Посмотреть данные пода:
```bash
$ kubectl describe pod my-nginx
Name:             my-nginx
Namespace:        default
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Fri, 10 Jul 2026 20:20:32 +0000
Labels:           run=my-nginx
Annotations:      <none>
Status:           Running
IP:               10.244.0.8
IPs:
  IP:  10.244.0.8
Containers:
  my-nginx:
    Container ID:   docker://4ffa9ebea307debc6ff58dcad54ffa74d08fe45771a64841abc59d890ae35aad
    Image:          nginx
    Image ID:       docker-pullable://nginx@sha256:ec4ed8b5299e5e90694af7750eb6dffd2627317d30544d056b0371f8082f7bce
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Fri, 10 Jul 2026 20:20:35 +0000
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-8fz9f (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
Volumes:
  kube-api-access-8fz9f:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  41m   default-scheduler  Successfully assigned default/my-nginx to minikube
  Normal  Pulling    41m   kubelet            spec.containers{my-nginx}: Pulling image "nginx"
  Normal  Pulled     41m   kubelet            spec.containers{my-nginx}: Successfully pulled image "nginx" in 1.258s (1.258s including waiting). Image size: 161308134 bytes.
  Normal  Created    41m   kubelet            spec.containers{my-nginx}: Container created
  Normal  Started    41m   kubelet            spec.containers{my-nginx}: Container started
```
```my-nginx``` – имя пода.

```Node``` – нода, на которой был создан под. Указаны имя и IP-адрес ноды.<br>
```IP``` – IP-адрес пода.<br>
```Containers``` – информация о контейнерах, запущенных в поде.<br>
```Events``` – логи жизненного цикла пода.

Сначала ```scheduler``` добавил под на определенную ноду (в примере «minikube»). Если бы количество нод было больше, то под мог бы быть создан на любой из этих нод. Далее был скачан образ «nginx», а также создан и запущен контейнер.

### Задача (Очистка): kubectl delete pod my-nginx. ###
```bash
$ kubectl get pods
NAME       READY   STATUS    RESTARTS      AGE
my-nginx   1/1     Running   1 (91s ago)   11h

$ kubectl delete pod my-nginx
pod "my-nginx" deleted from default namespace

$ kubectl get pods
No resources found in default namespace.
```
