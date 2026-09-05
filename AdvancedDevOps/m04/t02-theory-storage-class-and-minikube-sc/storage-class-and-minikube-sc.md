```StorageClass (SC)``` – объект «k8s», в котором указывается драйвер (```provisioner```) для динамического создания ```PV``` в заданной среде. Для «minikube» по умолчанию используется локальный ```SC``` с именем ```standard```:
```
provisioner: k8s.io/minikube-hostpath
```

```SC``` с индивидуальными настройками создается аналогично другим объектам «k8s» - с помощью декларативного описания (yaml).

Принцип работы:<br>
Для Пода создается ```PVC```, на основании которой ```SC``` создает ```PV``` с необходимыми характеристиками и в заданной среде.

Ключевые параметры:<br>
```provisioner``` – драйвер/провайдер, который будет создавать ```PV```.<br>
```reclaimPolicy``` – действия с ```PV``` после удаления ```PVC```:
* ```Delete``` – значение по умолчанию. ```PV``` будет удален.
* ```Retain``` - ```PV``` не удаляется, данные не очищаются.

```volumeBindingMode``` – когда ```PV``` привязывать к ```PVC```:
* ```Immediate``` – сразу после создания ```PVC```.
* ```WaitForFirstConsumer``` – после создания Пода, которому нужен ```PV```. При этом планировщик (```scheduler```) выберет оптимальную Ноду для создания ```PV```.

Команды:<br>
```kubectl get sc``` – список ```SC``` среды.

Пример:
```bash
$ kubectl get sc
NAME                 PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
standard (default)   k8s.io/minikube-hostpath   Delete          Immediate           false                  23h
```

```kubectl describe sc <имя>``` - параметры конкретного ```sc```.

Проверить привязку ```PV``` к ```PVC``` можно так:
```bash
$ kubectl get pvc
```
В колонке ```STATUS``` должно быть значение ```Bound``` (привязано).
