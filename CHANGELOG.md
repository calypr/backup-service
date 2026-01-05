# [1.14.0](https://github.com/calypr/backup-service/compare/v1.13.0...v1.14.0) (2026-01-05)


### Bug Fixes

* Add `gcc` dependency to Dockerfile for psycopg2 build ([5c0eebc](https://github.com/calypr/backup-service/commit/5c0eebc015c594f9dc39e5109d3fc703284d5984))
* Downgrade PostgreSQL in Backup Service to match Server version ([0b197fe](https://github.com/calypr/backup-service/commit/0b197fed399c51bb30c7330d9c7f89ab93171815))
* Remove `limit` parameter from Grip functions ([8473b3c](https://github.com/calypr/backup-service/commit/8473b3c87609865a8798271f968d990caeae1d23))
* Remove aced-submission dependency ([887a79c](https://github.com/calypr/backup-service/commit/887a79cb98c259c40baad5f93978bbc41d89128a))
* Remove PGPASSWORD parameters in favor of env vars ([53e2c7f](https://github.com/calypr/backup-service/commit/53e2c7fa0deb1d73077ab1783509af1e7916c529))
* Remove unused PGPASSWORD flag ([c650674](https://github.com/calypr/backup-service/commit/c650674190ce9e5477a4fe768cb165c1722bbdd5))
* Replace psycopg2-binary with psycopg2 to fix build errors ([7c027bd](https://github.com/calypr/backup-service/commit/7c027bde10f2c6b388e85b8e0b31ecff8c052862))
* update `pg_dump` env vars ([c9581a3](https://github.com/calypr/backup-service/commit/c9581a35385633aedbeeb9dfcece6ae4806fbebc))
* Update call to get edges to match latest syntax (`G.V().outE()`) ([0cbdd80](https://github.com/calypr/backup-service/commit/0cbdd8089e2ae0c47fa503a4354ba05b11aced51))
* Update Dockerfile ([2daf67f](https://github.com/calypr/backup-service/commit/2daf67f1046c7768dedcee2befef51f843ad8cf0))
* Update Dockerfile to include `pg_config` before Python build ([4e81901](https://github.com/calypr/backup-service/commit/4e819017583aeb7ca39160e9d09a805f8f5ef392))
* Update Dockerfile to install postgresql-client-14 ([581e39f](https://github.com/calypr/backup-service/commit/581e39f30407ba63aa82284b812e6863b5a85ab7))
* Update tests + re-add `--vertex` flag to GRIP command ([2b98f35](https://github.com/calypr/backup-service/commit/2b98f35837c6289b0ab7eaa518f01388f8cb8637))


### Features

* Add custom Elasticsearch Docker image with S3 Plugin installed ([4f2949d](https://github.com/calypr/backup-service/commit/4f2949d65a7ae93ab6596aff2810dd410b6c9ee8))
* Add initial support for Elastic Snapshot Restore ([645142d](https://github.com/calypr/backup-service/commit/645142df8adc105098fb2dbaafbcbab7d829f5f0))
* Add initial support for Elasticsearch snapshots ([5ae148f](https://github.com/calypr/backup-service/commit/5ae148f66ee0fd8ffed005447b01de445b345648))
* Add working ES snapshot repo initialization ([abeed25](https://github.com/calypr/backup-service/commit/abeed2574af3d9f4d40b8419581affede5bcba23))
* Move CLI functions to respective modules ([a7d2e67](https://github.com/calypr/backup-service/commit/a7d2e676905f871dab6620dd457371c2b8cc7bdf))
* Re-add support for ElasticSearch backups ([6db260b](https://github.com/calypr/backup-service/commit/6db260bb21a115056022b0943e345f85fe86d60a))
* Support env variables for S3 credentials ([4cddc79](https://github.com/calypr/backup-service/commit/4cddc797260a75e8178e3772ecf3ffd16f418b6e))
* Update call to GRIP edges ([35c70b4](https://github.com/calypr/backup-service/commit/35c70b46cad2a4858ea596e9d740ecf44686048b))
* Update entrypoint.sh ([9edb44c](https://github.com/calypr/backup-service/commit/9edb44c1ecae4afaa7b65e0976d0de97596fc793))

# [1.13.0](https://github.com/calypr/backup-service/compare/v1.12.1...v1.13.0) (2025-09-10)


### Features

* update entrypoint with GRIP limit variable ([bf2cf1d](https://github.com/calypr/backup-service/commit/bf2cf1d04cf37e02e276240f496336c727047efb))

## [1.12.1](https://github.com/calypr/backup-service/compare/v1.12.0...v1.12.1) (2025-09-10)


### Bug Fixes

* update output dir in entrypoint.sh ([3e67514](https://github.com/calypr/backup-service/commit/3e675144a6a2a84aa01e5300985862e764888cff))

# [1.12.0](https://github.com/calypr/backup-service/compare/v1.11.1...v1.12.0) (2025-09-10)


### Features

* add support for graph schemas in backups ([3f1b09e](https://github.com/calypr/backup-service/commit/3f1b09ef28018e32c6ba5633eb9fdc0ce262d59c))

## [1.11.1](https://github.com/calypr/backup-service/compare/v1.11.0...v1.11.1) (2025-09-10)


### Bug Fixes

* move timestamp logic from Python to entrypoint.sh ([513ca56](https://github.com/calypr/backup-service/commit/513ca56c9476fdc05798aa50d580b60f46236708))

# [1.11.0](https://github.com/calypr/backup-service/compare/v1.10.0...v1.11.0) (2025-09-10)


### Features

* update entrypoint.sh ([96e3d1a](https://github.com/calypr/backup-service/commit/96e3d1a6d18701024bd22a757d51ccff364a20f5))

# [1.10.0](https://github.com/calypr/backup-service/compare/v1.9.0...v1.10.0) (2025-09-10)


### Features

* add commit tagging to Docker images ([42780a5](https://github.com/calypr/backup-service/commit/42780a5865a511039e4eb3557d5e94c0546219d0))
* add GRIP build to Dockerfile ([98ce9a6](https://github.com/calypr/backup-service/commit/98ce9a683bd2e9e9933b42544292984b32ec0780))
* add initial GRIP backup commands ([14e5eba](https://github.com/calypr/backup-service/commit/14e5ebac88d54edee245fca52716a1661463d40e))
* Add initial GRIP ls command for listing graphs and edges ([547aa5a](https://github.com/calypr/backup-service/commit/547aa5aa1807538e9234e82f11fe5c708b1c81a7))
* update GRIP backup logic ([12147e6](https://github.com/calypr/backup-service/commit/12147e68c4f340ad7f06b2148b7e144d7a5ef86a))

# [1.9.0](https://github.com/calypr/backup-service/compare/v1.8.1...v1.9.0) (2025-07-30)


### Features

* update README ([458979b](https://github.com/calypr/backup-service/commit/458979bf470f2ee2c47a14760869a5913f12f05a))

## [1.8.1](https://github.com/calypr/backup-service/compare/v1.8.0...v1.8.1) (2025-07-29)


### Bug Fixes

* update S3 upload/download ([400181b](https://github.com/calypr/backup-service/commit/400181ba178805c44b2f18e85f9081848f01c174))

# [1.8.0](https://github.com/calypr/backup-service/compare/v1.7.0...v1.8.0) (2025-07-16)


### Features

* update Elasticsearch backup configuration ([dea977e](https://github.com/calypr/backup-service/commit/dea977efb57b030884c39cbd94e360e0d1786e3b))

# [1.7.0](https://github.com/ACED-IDP/backup-service/compare/v1.6.0...v1.7.0) (2025-07-14)


### Features

* update module imports ([ac575ae](https://github.com/ACED-IDP/backup-service/commit/ac575ae3359994209a846ad789400db5b0542ca5))

# [1.6.0](https://github.com/ACED-IDP/backup-service/compare/v1.5.0...v1.6.0) (2025-07-09)


### Features

* Add entrypoint script for backup process ([a6cb424](https://github.com/ACED-IDP/backup-service/commit/a6cb4247561b6bb411849a40689aa9fc6475a289))

# [1.5.0](https://github.com/ACED-IDP/backup-service/compare/v1.4.1...v1.5.0) (2025-07-08)


### Features

* add initial ElasticSearch module ([1cf6e2e](https://github.com/ACED-IDP/backup-service/commit/1cf6e2e89702cab042315d2e7ff3dd73d03c27c0))

## [1.4.1](https://github.com/ACED-IDP/backup-service/compare/v1.4.0...v1.4.1) (2025-07-02)


### Bug Fixes

* temp tests for backup service ([039a3ab](https://github.com/ACED-IDP/backup-service/commit/039a3ab290b41a2b2ad5aa7d127e3f0de700af7e))

# [1.4.0](https://github.com/ACED-IDP/backup-service/compare/v1.3.2...v1.4.0) (2025-07-02)


### Features

* add initial restore functionality ([4fbf878](https://github.com/ACED-IDP/backup-service/commit/4fbf878a478a68507e7f71d9b9be7137a7ee7fbb))

## [1.3.2](https://github.com/ACED-IDP/backup-service/compare/v1.3.1...v1.3.2) (2025-07-01)


### Bug Fixes

* update upload operation ([8424065](https://github.com/ACED-IDP/backup-service/commit/8424065080caa0c6aa51b1f9e8b29893c76ae978))

## [1.3.1](https://github.com/ACED-IDP/backup-service/compare/v1.3.0...v1.3.1) (2025-07-01)


### Bug Fixes

* update example notebook ([d45ebd1](https://github.com/ACED-IDP/backup-service/commit/d45ebd105fad15877be4e7dc380e853519d8b5a7))

# [1.3.0](https://github.com/ACED-IDP/backup-service/compare/v1.2.2...v1.3.0) (2025-07-01)


### Features

* add initial example python notebook ([488f5e6](https://github.com/ACED-IDP/backup-service/commit/488f5e65a42c9dc230fc59da0b60db2c0956af65))

## [1.2.2](https://github.com/ACED-IDP/backup-service/compare/v1.2.1...v1.2.2) (2025-07-01)


### Bug Fixes

* update requirements.txt ([ddc7a09](https://github.com/ACED-IDP/backup-service/commit/ddc7a09f4f2863d6c37849294910df81af5768cf))

## [1.2.1](https://github.com/ACED-IDP/backup-service/compare/v1.2.0...v1.2.1) (2025-07-01)


### Bug Fixes

* Update README and backup scripts ([7d08aef](https://github.com/ACED-IDP/backup-service/commit/7d08aef1f7a74e9bd484124f5a1bb9c8b300aba1))

# [1.2.0](https://github.com/ACED-IDP/backup-service/compare/v1.1.0...v1.2.0) (2025-07-01)


### Features

* add initial logging ([f8c97e9](https://github.com/ACED-IDP/backup-service/commit/f8c97e93bc06ad311ffade16b8d22077db3f2604))
* update backup functionality ([ac81457](https://github.com/ACED-IDP/backup-service/commit/ac8145758684fe8d25b29d112c8d1c2ff7d86ac4))

# [1.1.0](https://github.com/ACED-IDP/backup-service/compare/v1.0.2...v1.1.0) (2025-06-25)


### Features

* Add backup functionality and tests ([de3352c](https://github.com/ACED-IDP/backup-service/commit/de3352cbd7801c5fcfe0603cd1a4add5fcf176ac))

## [1.0.2](https://github.com/ACED-IDP/backup-service/compare/v1.0.1...v1.0.2) (2025-06-24)


### Bug Fixes

* Update tests ([34b4c3e](https://github.com/ACED-IDP/backup-service/commit/34b4c3e049f868135c99022ba1a917ee33f049b8))

## [1.0.1](https://github.com/ACED-IDP/backup-service/compare/v1.0.0...v1.0.1) (2025-06-23)


### Bug Fixes

* Update workflow and release configuration ([8697490](https://github.com/ACED-IDP/backup-service/commit/86974908013b55e79033538f0a8ceb7661d0a9d8))

# 1.0.0 (2025-06-23)


### Bug Fixes

* update tests and dependencies ([f450828](https://github.com/ACED-IDP/backup-service/commit/f450828ed436cdfa0a361551753db1e47d4d6ae0))
