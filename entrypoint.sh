#!/bin/bash
set -e

TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")

# Default operation is backup, but can be overridden with OPERATION env var
OPERATION=${OPERATION:-backup}

export DIR="${DIR}/${TIMESTAMP}"

if [ "$OPERATION" = "backup" ]; then
    echo "Starting backup operation..."
    
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
        --limit "${GRIP_LIMIT}" \
        --vertex \
        --edge

    # S3 Upload
    bak --debug s3 upload \
        --dir "${DIR}" \
        --endpoint "${ENDPOINT}" \
        --bucket "${BUCKET}" \
        --key "${KEY}" \
        --secret "${SECRET}"
        
    echo "Backup operation completed successfully"

elif [ "$OPERATION" = "restore" ]; then
    echo "Starting restore operation..."
    
    # S3 Download - restore from specified backup directory or latest
    RESTORE_DIR=${RESTORE_DIR:-"${DIR}"}
    
    bak --debug s3 download \
        --dir "${RESTORE_DIR}" \
        --endpoint "${ENDPOINT}" \
        --bucket "${BUCKET}" \
        --key "${KEY}" \
        --secret "${SECRET}"

    # Postgres Restore
    bak --debug pg restore \
        --dir "${RESTORE_DIR}" \
        --host "${PGHOST}" \
        --user "${PGUSER}" \
        --password "${PGPASSWORD}"

    # GRIP Restore
    bak --debug grip restore \
        --dir "${RESTORE_DIR}" \
        --host "${GRIP_HOST}" \
        --graph "${GRIP_GRAPH}"
        
    echo "Restore operation completed successfully"

else
    echo "Error: Unknown operation '${OPERATION}'. Valid operations are 'backup' or 'restore'"
    exit 1
fi
