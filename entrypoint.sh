#!/bin/bash
set -e

echo "Backup started at $(date)"

# Postgres Dump
echo "Running Postgres dump..."
bak --debug pg dump \
    --host "${PGHOST}" \
    --user "${PGUSER}" \
    --password "${PGPASSWORD}" \
    --dir "${DIR}"

# S3 Upload
echo "Running S3 upload..."
bak --debug pg upload \
    --dir "${DIR}" \
    --bucket "${BUCKET}" \
    --endpoint "${ENDPOINT}" \
    --key "${KEY}" \
    --secret "${SECRET}"

echo "Backup completed at $(date)"
