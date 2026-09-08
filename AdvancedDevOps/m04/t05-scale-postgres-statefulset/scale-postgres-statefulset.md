Масштабируем количество Подов:
```bash
$ kubectl scale statefulset pg --replicas=3
statefulset.apps/pg scaled
```

В другом терминале можно в режиме реального времени наблюдать за созданием и запуском Подов:
```bash
$ kubectl get pods -w
NAME   READY   STATUS    RESTARTS       AGE
pg-0   1/1     Running   2 (103s ago)   13h
pg-1   0/1     Pending   0              0s
pg-1   0/1     ContainerCreating   0              13s
pg-1   1/1     Running             0              15s
pg-2   0/1     Pending             0              0s
pg-2   0/1     ContainerCreating   0              0s
pg-2   1/1     Running             0              7s
```

Видно, что Поды запускаются последовательно.<br>
В итоге будут запущены 3 Пода и созданы диски к ним:
```bash
$ kubectl get pods
NAME   READY   STATUS    RESTARTS        AGE
pg-0   1/1     Running   2 (8m43s ago)   13h
pg-1   1/1     Running   0               6m36s
pg-2   1/1     Running   0               6m21s

$ kubectl get pvc
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS
   VOLUMEATTRIBUTESCLASS   AGE
data-pg-0   Bound    pvc-b08baa2e-1534-4756-89e3-0b8a97eddff1   1Gi        RWO            standard
   <unset>                 13h
data-pg-1   Bound    pvc-99bde255-f01f-4153-a164-f6c00ad6bd3d   1Gi        RWO            standard
   <unset>                 6m39s
data-pg-2   Bound    pvc-9aea53e1-561a-424b-950e-1189a4e10caf   1Gi        RWO            standard
   <unset>                 6m24s
```

Посмотрим Поды ```StatefulSet```:
```bash
$ kubectl get statefulset pg
NAME   READY   AGE
pg     3/3     13h
```

Проверим данные примонтированного тома у одного из Подов:
```bash
$ kubectl exec -it pg-0 -- df -h /var/lib/postgresql/data
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda2        50G   27G   21G  57% /var/lib/postgresql/data
```

Видно, что размер диска 50 Гб, хотя в заявке был 1 Гб. Это особенность работы «minikube» - создается не отдельный диск, а каталог, который монтируется в Под. Поэтому команда ```df``` показывает размер всего диска, на котором находится этот каталог.

Проверим данные созданного Тома:
```bash
$ kubectl get pvc data-pg-0
NAME        STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS
   VOLUMEATTRIBUTESCLASS   AGE
data-pg-0   Bound    pvc-b08baa2e-1534-4756-89e3-0b8a97eddff1   1Gi        RWO            standard
   <unset>                 14h

$ kubectl describe pv $(kubectl get pvc data-pg-0 -o jsonpath='{.spec.volumeName}')
Name:            pvc-b08baa2e-1534-4756-89e3-0b8a97eddff1
Labels:          <none>
Annotations:     hostPathProvisionerIdentity: cc8c20f6-ebc2-412c-a8ef-0875932a9fda
                 pv.kubernetes.io/provisioned-by: k8s.io/minikube-hostpath
Finalizers:      [kubernetes.io/pv-protection]
StorageClass:    standard
Status:          Bound
Claim:           default/data-pg-0
Reclaim Policy:  Delete
Access Modes:    RWO
VolumeMode:      Filesystem
Capacity:        1Gi
Node Affinity:   <none>
Message:
Source:
    Type:          HostPath (bare host directory volume)
    Path:          /tmp/hostpath-provisioner/default/data-pg-0
    HostPathType:
Events:            <none>
```

Видим, что размер 1 Гб. Также можно посмотреть другую информацию о Томе, например, расположение каталога, в котором он находится (```Source/Path```).
