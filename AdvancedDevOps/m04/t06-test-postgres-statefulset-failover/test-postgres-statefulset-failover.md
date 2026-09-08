Создадим текстовый файл на Томе Пода ```pg-1```:
```bash
$ kubectl exec pg-1 -- sh -c 'echo "marker: written BEFORE failover" > 
    /var/lib/postgresql/data/failover-marker.txt'
```

Проверим метку:
```bash
$ kubectl exec pg-1 -- cat /var/lib/postgresql/data/failover-marker.txt
marker: written BEFORE failover
```

```/var/lib/postgresql/data``` – примонтированный диск ```data-pg-1```. Все, что находится в этом каталоге, хранится на ```PVC```, а не в контейнере.

Удалим Под:
```bash
$ kubectl delete pod pg-1
pod "pg-1" deleted from default namespace
```

При наблюдении за Подами в реальном времени, будут выведены следующие данные:
```bash
$ kubectl get pods -w
NAME   READY   STATUS              RESTARTS        AGE
pg-0   1/1     Running             2 (4h19m ago)   17h
pg-1   1/1     Running             0               4h17m
pg-2   1/1     Running             0               4h17m
pg-1   1/1     Terminating         0               4h17m
pg-1   0/1     Completed           0               4h17m
pg-1   0/1     Pending             0               0s
pg-1   0/1     ContainerCreating   0               1s
pg-1   1/1     Running             0               5s
```

Снова проверим метку:
```bash
$ kubectl exec pg-1 -- cat /var/lib/postgresql/data/failover-marker.txt
marker: written BEFORE failover
```

Метка осталась – диск ```data-pg-1``` переподключился к новому Поду. Данные не потеряны.

Проверим диски:
```bash
$ kubectl get pvc
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS
   VOLUMEATTRIBUTESCLASS   AGE
data-pg-0   Bound    pvc-b08baa2e-1534-4756-89e3-0b8a97eddff1   1Gi        RWO            standard
   <unset>                 17h
data-pg-1   Bound    pvc-99bde255-f01f-4153-a164-f6c00ad6bd3d   1Gi        RWO            standard
   <unset>                 4h23m
data-pg-2   Bound    pvc-9aea53e1-561a-424b-950e-1189a4e10caf   1Gi        RWO            standard
   <unset>                 4h23m
```

По времени существования видно, что диск ```data-pg-1``` не пересоздавался.
