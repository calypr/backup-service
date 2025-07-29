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

echo "Backup completed at $(date)"
