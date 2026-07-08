Packages:
```
m08-t08-multi-arch-build 748e724d26b2f60382975b21c5649c81cb51524c
```

Installation:
```
docker pull ghcr.io/aesh-sudo/m08-t08-multi-arch-build:748e724d26b2f60382975b21c5649c81cb51524c
```
OS/Arch:
```
linux/amd64
$ docker pull ghcr.io/aesh-sudo/m08-t08-multi-arch-build:748e724d2
6b2f60382975b21c5649c81cb51524c@sha256:e2b694eb1e0085632084b4f623da42df0642a914838dcaeb0353323a52ba8a79

linux/arm64
$ docker pull ghcr.io/aesh-sudo/m08-t08-multi-arch-build:748e724d2
6b2f60382975b21c5649c81cb51524c@sha256:bf4d36f7b791ae88ff94e1e598a456ab95994b9e5f57b87eee91065fd80e29e9

unknown/unknown
$ docker pull ghcr.io/aesh-sudo/m08-t08-multi-arch-build:748e724d2
6b2f60382975b21c5649c81cb51524c@sha256:2c0c10f18acd19de0b40b2549a55115b3f5b8280b1f8b03e08642262c53f41ac
```

Проверим манифесты:
```
$ docker buildx imagetools inspect ghcr.io/aesh-sudo/m08-t08-multi-arch-build:latest
Name:      ghcr.io/aesh-sudo/m08-t08-multi-arch-build:latest
MediaType: application/vnd.oci.image.index.v1+json
Digest:    sha256:2dccad3ba7260edce47e808c93dbd386479d71514f5a862d25198f061f3a273b

Manifests:
  Name:        ghcr.io/aesh-sudo/m08-t08-multi-arch-build:latest@sha256:
e2b694eb1e0085632084b4f623da42df0642a914838dcaeb0353323a52ba8a79
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/amd64

  Name:        ghcr.io/aesh-sudo/m08-t08-multi-arch-build:latest@sha256:
bf4d36f7b791ae88ff94e1e598a456ab95994b9e5f57b87eee91065fd80e29e9
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    linux/arm64

  Name:        ghcr.io/aesh-sudo/m08-t08-multi-arch-build:latest@sha256:
2c0c10f18acd19de0b40b2549a55115b3f5b8280b1f8b03e08642262c53f41ac
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    unknown/unknown
  Annotations:
    vnd.docker.reference.digest: sha256:e2b694eb1e0085632084b4f623da42df0642a914838dcaeb0353323a52ba8a79
    vnd.docker.reference.type:   attestation-manifest

  Name:        ghcr.io/aesh-sudo/m08-t08-multi-arch-build:latest@sha256:
2eb3b84e6d33b5be32f7990cafdc4c23bc087e902adb8ffc36ce18e7dbf2542a
  MediaType:   application/vnd.oci.image.manifest.v1+json
  Platform:    unknown/unknown
  Annotations:
    vnd.docker.reference.digest: sha256:bf4d36f7b791ae88ff94e1e598a456ab95994b9e5f57b87eee91065fd80e29e9
    vnd.docker.reference.type:   attestation-manifest
```

То есть, у нас получилось два образа и две аттестации к ним. Аттестация – информация о том, где и как был собран образ, представленная в JSON-виде:
* Какой «GitHub Actions workflow» собрал образ.
* Какой был «commit SHA».
* На каком runner'е собирался образ.
* Какие были входные параметры.
* Временные метки.
