# Contributing

# CLI

## Install

```sh
➜ git clone git@github.com:calypr/backup-service

➜ cd backup-service

➜ python3 -m venv venv && source venv/bin/activate

➜ pip install -r requirements.txt

➜ pip install -e .

➜ which bak
./venv/bin/bak

➜ bak --help
Usage: bak [OPTIONS] COMMAND [ARGS]...

Options:
  --version               Show the version and exit.
  -v, --verbose, --debug  Enable debug logging.
  --help                  Show this message and exit.

Commands:
  grip (gp)  Commands for GRIP backups.
  pg (pg)    Commands for Postgres backups.
  s3         Commands for S3.
```

## PostgreSQL 

| Command     | Example          |
|-------------|------------------|
| List Tables | `bak pg ls`      |
| Backup      | `bak pg dump`    |
| Restore     | `bak pg restore` |

## GRIP

| Command     | Example            |
|-------------|--------------------|
| List Graphs | `bak grip ls`      |
| Backup      | `bak grip backup`  |
| Restore     | `bak grip restore` |

## S3

| Command      | Example           |
|--------------|-------------------|
| List backups | `bak s3 ls`       |
| Upload       | `bak s3 upload`   |
| Download     | `bak s3 download` |

# Helm

```sh
➜ helm repo add ohsu https://ohsu-comp-bio.github.io/helm-charts
"ohsu" has been added to your repositories

➜ helm repo update ohsu
Update Complete. ⎈Happy Helming!⎈

➜ helm search repo ohsu
NAME                    CHART VERSION   APP VERSION     DESCRIPTION
ohsu/backups            0.2.5           1.13.0          A Helm chart for Kubernetes

➜ kubectl config current-context
kind-dev

➜ kubectl create secret generic postgres-credentials --from-literal=postgres-password=<PGPASSWORD> --namespace backups

➜ kubectl create secret generic s3-credentials --from-literal=AWS_ACCESS_KEY=<KEY> --from-literal=AWS_SECRET_KEY=<SECRET> --namespace backups

➜ helm upgrade --install backups ohsu/backups --create-namespace --namespace backups
Release "backups" has been upgraded. Happy Helming!

➜ kubectl create job example-job --from=cronjob/backup-service-cronjob --namespace backups
job.batch/example-job created

➜ kubectl get jobs -n backups
NAME          STATUS     COMPLETIONS   DURATION
example-job   Complete   1/1           11s

➜ mc ls cbds/calypr-backups/calypr-dev
2025-09-12T23:10:29/

➜ mc ls cbds/calypr-backups/calypr-dev/2025-09-12T23:10:29/
CALYPR.edges
CALYPR.vertices
CALYPR__schema__.edges
CALYPR__schema__.vertices
arborist_local.sql
fence_local.sql
gecko_local.sql
indexd_local.sql
postgres.sql
requestor_local.sql
```

* Steps to confirm backups in S3 bucket with mc

```sh
➜ brew install minio-mc

➜ which mc
/opt/homebrew/bin/mc

➜ mc alias set example https://aced-storage.ohsu.edu
Enter Access Key: <KEY>
Enter Secret Key:
Added `example` successfully.

➜ mc alias ls example
cbds
  URL       : https://aced-storage.ohsu.edu
  AccessKey : <KEY>
  SecretKey : <SECRET>
  API       : s3v4
  Path      : auto
  Src       : $HOME/.mc/config.json

➜ mc ls cbds/calypr-backups/calypr-dev/
...
2025-09-12T02:00:01/  <---- Last timestamped backup

➜ mc ls cbds/calypr-backups/calypr-dev/2025-09-12T02:00:01/
160MiB  CALYPR.edges               <---- CALYPR edges
1.8GiB  CALYPR.vertices            <---- CALYPR vertices
    0B  CALYPR__schema__.edges     <---- Schema edges
1.4MiB  CALYPR__schema__.vertices  <---- Schema vertices
107KiB  arborist_local.sql         <---- Arborist
234KiB  fence_local.sql            <---- Fence
6.0KiB  gecko_local.sql            <---- Gecko
 21MiB  indexd_local.sql           <---- Indexd
9.6KiB  metadata_local.sql         <---- Metadata
2.9KiB  postgres.sql               <---- Postgres
 64KiB  requestor_local.sql        <---- Requestor
8.0KiB  wts_local.sql              <---- Workspace Token Service
```

# Known Limitations (Next Steps) ⚠️

- [ ] No clear, human-readable output of the path of the backup in S3 after a successful run
- [ ] Always uploads to calypr-dev even when using local k8s cluster
