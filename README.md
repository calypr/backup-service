[![License: Apache 2.0][license-badge]][license]
[![GitHub Release][release-badge]][release]
[![Docker][docker-badge]][docker]
[![Helm][helm-badge]][helm]

[license-badge]: https://img.shields.io/badge/License-Apache-blue.svg
[license]: https://opensource.org/license/apache-2-0
[release-badge]: https://img.shields.io/github/v/release/ACED-IDP/backup-service
[release]: https://github.com/ACED-IDP/backup-service/releases
[docker-badge]: https://img.shields.io/badge/Docker%20Repo-Quay.io-blue?logo=docker
[docker]: https://quay.io/repository/ohsu-comp-bio/backup-service?tab=tags&tag=latest
[helm-badge]: https://img.shields.io/badge/Helm-0F1689?logo=helm&logoColor=fff
[helm]: https://github.com/ohsu-comp-bio/helm-charts/tree/main/charts/backups

# 2. Overview ⚙️

Data backup and recovery service for the CALYPR systems 🔄

## Backups ↩️

| Service   | Postgres Database   | S3 Bucket                     |
| --------- | ------------------- | ----------------------------- |
| Arborist  | `arborist-EXAMPLE`  | `arborist-EXAMPLE-TIMESTAMP`  |
| Fence     | `fence-EXAMPLE`     | `fence-EXAMPLE-TIMESTAMP`     |
| Gecko     | `gecko-EXAMPLE`     | `gecko-EXAMPLE-TIMESTAMP`     |
| Indexd    | `indexd-EXAMPLE`    | `indexd-EXAMPLE-TIMESTAMP`    |
| Requestor | `requestor-EXAMPLE` | `requestor-EXAMPLE-TIMESTAMP` |

# 2. Quick Start ⚡

```sh
➜ chmod +x main.sh

➜ ./main.sh
```

# 3. Additional Resources 📚

- Gen3 Graph Data Flow:

  > https://docs.gen3.org/gen3-resources/developer-guide/architecture/#gen3-graph-data-flow

- Data Submission System (legacy docs):

  > https://gen3.org/resources/developer/#data-submission-system

- Gen3’s Microservices (legacy docs):
  > https://gen3.org/resources/developer/microservice/
