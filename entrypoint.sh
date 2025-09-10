#!/bin/bash
set -e

echo "Backup started at $(date)"

# Postgres Dump
echo "Running Postgres dump..."
bak --debug pg dump \
    --dir "${DIR}" \
    --host "${PGHOST}" \
    --user "${PGUSER}" \
    --password "${PGPASSWORD}"

# S3 Upload
echo "Running S3 upload..."
bak --debug s3 upload \
    --dir "${DIR}" \
    --endpoint "${ENDPOINT}" \
    --bucket "${BUCKET}" \
    --key "${KEY}" \
    --secret "${SECRET}"

echo "Postgres Backup completed at $(date)"

# GRIP Backup
echo "Running GRIP backup..."
bak --debug grip backup \
    --dir "${DIR}" \
    --host "${GRIP_HOST}" \
    --graph "${GRIP_GRAPH}" \
    --vertex \
    --edge

# S3 Upload
echo "Running S3 upload..."
bak --debug s3 upload \
    --dir "${DIR}" \
    --endpoint "${ENDPOINT}" \
    --bucket "${BUCKET}" \
    --key "${KEY}" \
--secret "${SECRET}"

echo "GRIP Backup completed at $(date)"
