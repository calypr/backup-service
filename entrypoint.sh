#!/bin/bash
set -eio pipefail

trap 'echo "Backup failed."; exit 1' ERR

#  Backup Overview/Structure:
# 
#  ENDPOINT/BUCKET/TIMESTAMP
#  │
#  ├─ elastic
#  │  ├─ TODO
#  │  └─ TODO
#  │
#  ├─ grip
#  │  ├─ CALYPR.edges
#  │  └─ CALYPR.vertices
#  │
#  └─ postgres
#     ├─ arborist_local.sql
#     ├─ fence_local.sql
#     ├─ gecko_local.sql
#     ├─ indexd_local.sql
#     ├─ metadata_local.sql
#     ├─ postgres.sql
#     ├─ requestor_local.sql
#     └─ wts_local.sql

TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")

export DIR="${DIR}/${TIMESTAMP}"

# 1. Postgres Dump
bak --debug pg dump \
    --dir "${DIR}" \
    --host "${PGHOST}" \
    --user "${PGUSER}"

# 2. GRIP Backup
bak --debug grip backup \
    --dir "${DIR}" \
    --host "${GRIP_HOST}" \
    --graph "${GRIP_GRAPH}" \
    --vertex \
    --edge

# 3. S3 Upload
bak --debug s3 upload \
    --dir "${DIR}" \
    --endpoint "${ENDPOINT}" \
    --bucket "${BUCKET}" \
    --key "${ACCESS_KEY}" \
    --secret "${SECRET_KEY}"

# 4. Elasticsearch Snapshot
# We keep the Elasticsearch backups separate from that of Postgres and GRIP
# to conform to the standard snapshot behavior/structure (e.g. incremental diffs)
# Ref: https://www.elastic.co/docs/deploy-manage/tools/snapshot-and-restore/self-managed
bak --debug es dump \
    --endpoint "${ES_ENDPOINT}" \
    --bucket "${ES_BUCKET}" \
    --repo "${ES_REPO}" \
    --snapshot "${DIR}" \

echo "Backup Complete:"
echo "- ENDPOINT: ${ENDPOINT}"
echo "- BUCKET: ${BUCKET}"
echo "- DIR: ${DIR}"
