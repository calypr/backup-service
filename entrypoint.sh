#!/bin/bash
set -e

TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")

DIR="${DIR/$TIMESTAMP}"

# Postgres Dump
bak --debug pg dump \
    --dir "${DIR}" \
    --host "${PGHOST}" \
    --user "${PGUSER}" \
    --password "${PGPASSWORD}"

# GRIP Backup
bak --debug grip backup \
    --dir "${DIR}" \
    --host "${GRIP_HOST}" \
    --graph "${GRIP_GRAPH}" \
    --vertex \
    --edge

# S3 Upload
bak --debug s3 upload \
    --dir "${DIR}" \
    --endpoint "${ENDPOINT}" \
    --bucket "${BUCKET}" \
    --key "${KEY}" \
    --secret "${SECRET}"
