#!/bin/bash
set -e

echo "Backup started at $(date)"

# Postgres Dump
echo "Running Postgres dump..."
bak --debug pg dump \
    --host "${PGHOST}" \
    --port "${PGPORT}" \
    --user "${PGUSER}" \
    --dir "/backups"

# S3 Upload
echo "Running S3 upload..."
bak --debug s3 upload \
    --dir "/backups" \
    --bucket "${BUCKET}" \
    --endpoint "${ENDPOINT}"

echo "Backup completed at $(date)"
