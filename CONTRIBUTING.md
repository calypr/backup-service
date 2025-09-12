# Contributing to Backup Service

Welcome to the backup-service project! This guide will help you get started with installing, running, and deploying the backup service for CALYPR systems. 🔄

## Table of Contents

- [Manual Installation & CLI Usage](#manual-installation--cli-usage)
- [Kubernetes Deployment with Helm](#kubernetes-deployment-with-helm)
- [Verifying S3 Backups](#verifying-s3-backups)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)

## Manual Installation & CLI Usage

### Prerequisites

- **Python 3.12+** is required
- **PostgreSQL client tools** (for database operations)
- **Docker** (optional, for containerized usage)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/calypr/backup-service.git
   cd backup-service
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Install the backup service:**
   ```bash
   pip install -e .
   ```

5. **Verify installation:**
   ```bash
   bak --help
   ```

### CLI Usage Examples

#### PostgreSQL Operations

**List databases:**
```bash
bak pg ls \
  --host localhost \
  --port 5432 \
  --user postgres \
  --password your_password
```

**Dump all databases to local directory:**
```bash
bak pg dump \
  --host localhost \
  --port 5432 \
  --user postgres \
  --password your_password \
  --dir /path/to/backup/directory
```

**Restore databases from local directory:**
```bash
bak pg restore \
  --host localhost \
  --port 5432 \
  --user postgres \
  --password your_password \
  --dir /path/to/backup/directory
```

#### S3 Operations

**Upload backups to S3:**
```bash
bak s3 upload \
  --endpoint https://s3.amazonaws.com \
  --bucket your-backup-bucket \
  --key your-access-key \
  --secret your-secret-key \
  --dir /path/to/backup/directory
```

**Download backups from S3:**
```bash
bak s3 download \
  --endpoint https://s3.amazonaws.com \
  --bucket your-backup-bucket \
  --key your-access-key \
  --secret your-secret-key \
  --dir /path/to/restore/directory
```

#### GRIP Operations

**Backup GRIP database:**
```bash
bak grip backup \
  --host localhost \
  --port 8201 \
  --graph your-graph-name \
  --dir /path/to/backup/directory \
  --vertices \
  --edges
```

**Restore GRIP database:**
```bash
bak grip restore \
  --host localhost \
  --port 8201 \
  --graph your-graph-name \
  --dir /path/to/backup/directory
```

### Docker Usage

You can also run the backup service using Docker:

```bash
# Build the Docker image
docker build -t backup-service .

# Run a backup operation
docker run --rm \
  -v /host/backup/path:/backups \
  backup-service bak pg dump \
  --host database-host \
  --port 5432 \
  --user postgres \
  --password password \
  --dir /backups
```

## Kubernetes Deployment with Helm

### Prerequisites

- **kubectl** configured with access to your Kubernetes cluster
- **Helm 3.x** installed
- Access to the **ohsu-comp-bio/helm-charts** repository

### Helm Installation Steps

1. **Add the Helm repository:**
   ```bash
   helm repo add ohsu-comp-bio https://ohsu-comp-bio.github.io/helm-charts
   helm repo update
   ```

2. **Create a values file for your deployment:**
   ```bash
   cat > backup-values.yaml << EOF
   image:
     repository: quay.io/ohsu-comp-bio/backup-service
     tag: "latest"
     pullPolicy: Always

   # Configure backup schedule as a CronJob
   schedule: "0 2 * * *"  # Daily at 2 AM

   # Environment variables for database connection
   env:
     - name: POSTGRES_HOST
       value: "postgres-service.default.svc.cluster.local"
     - name: POSTGRES_PORT
       value: "5432"
     - name: POSTGRES_USER
       valueFrom:
         secretKeyRef:
           name: postgres-secret
           key: username
     - name: POSTGRES_PASSWORD
       valueFrom:
         secretKeyRef:
           name: postgres-secret
           key: password

   # S3 configuration
     - name: S3_ENDPOINT
       value: "s3.amazonaws.com"
     - name: S3_BUCKET
       value: "your-backup-bucket"
     - name: AWS_ACCESS_KEY_ID
       valueFrom:
         secretKeyRef:
           name: s3-secret
           key: access-key
     - name: AWS_SECRET_ACCESS_KEY
       valueFrom:
         secretKeyRef:
           name: s3-secret
           key: secret-key

   # Resource limits
   resources:
     limits:
       cpu: 500m
       memory: 512Mi
     requests:
       cpu: 100m
       memory: 128Mi

   # Persistent volume for temporary backup storage
   persistence:
     enabled: true
     size: 10Gi
     storageClass: "standard"
   EOF
   ```

3. **Create necessary secrets:**
   ```bash
   # PostgreSQL credentials
   kubectl create secret generic postgres-secret \
     --from-literal=username=postgres \
     --from-literal=password=your-postgres-password

   # S3 credentials
   kubectl create secret generic s3-secret \
     --from-literal=access-key=your-access-key \
     --from-literal=secret-key=your-secret-key
   ```

4. **Install the Helm chart:**
   ```bash
   helm install backup-service ohsu-comp-bio/backups \
     --values backup-values.yaml \
     --namespace backup-system \
     --create-namespace
   ```

5. **Verify the deployment:**
   ```bash
   kubectl get pods -n backup-system
   kubectl get cronjobs -n backup-system
   kubectl logs -n backup-system deployment/backup-service
   ```

### Helm Chart Configuration

The backup service Helm chart supports the following key configurations:

- **Schedule**: Configure CronJob schedule for automated backups
- **Image**: Specify the backup service container image
- **Environment**: Database and S3 connection parameters
- **Resources**: CPU and memory limits/requests
- **Persistence**: Temporary storage for backup files
- **Security**: Pod security context and service account configuration

For complete configuration options, see: https://github.com/ohsu-comp-bio/helm-charts/tree/main/charts/backups

## Verifying S3 Backups

### Using AWS CLI

1. **Install AWS CLI:**
   ```bash
   pip install awscli
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   # Enter your Access Key ID, Secret Access Key, region, and output format
   ```

3. **List backup files:**
   ```bash
   # List all backups in your bucket
   aws s3 ls s3://your-backup-bucket/

   # List backups with timestamps
   aws s3 ls s3://your-backup-bucket/ --recursive --human-readable

   # List specific database backups
   aws s3 ls s3://your-backup-bucket/postgres/ --recursive
   ```

4. **Download and verify backup content:**
   ```bash
   # Download a specific backup
   aws s3 cp s3://your-backup-bucket/postgres/database-2024-01-15.sql.gz ./

   # Verify the backup file
   gunzip database-2024-01-15.sql.gz
   head -50 database-2024-01-15.sql  # Check backup contents
   ```

5. **Check backup sizes and dates:**
   ```bash
   # Get detailed information about backups
   aws s3api list-objects-v2 \
     --bucket your-backup-bucket \
     --prefix postgres/ \
     --query 'Contents[?Size>`1000000`].[Key,Size,LastModified]' \
     --output table
   ```

### Using MinIO Client (mc)

1. **Install MinIO client:**
   ```bash
   # Linux/macOS
   curl https://dl.min.io/client/mc/release/linux-amd64/mc \
     --create-dirs -o ~/bin/mc
   chmod +x ~/bin/mc

   # Or via package manager
   brew install minio/stable/mc  # macOS
   ```

2. **Configure MinIO client:**
   ```bash
   # For AWS S3
   mc alias set aws https://s3.amazonaws.com your-access-key your-secret-key

   # For MinIO server
   mc alias set minio https://your-minio-server.com your-access-key your-secret-key
   ```

3. **List and verify backups:**
   ```bash
   # List all backups
   mc ls aws/your-backup-bucket/

   # List with details
   mc ls --recursive --summarize aws/your-backup-bucket/

   # Find backups by date
   mc find aws/your-backup-bucket/ --name "*2024-01*" --print
   ```

4. **Download and verify backup content:**
   ```bash
   # Download a backup
   mc cp aws/your-backup-bucket/postgres/database-2024-01-15.sql.gz ./

   # Compare backup sizes
   mc stat aws/your-backup-bucket/postgres/database-2024-01-15.sql.gz
   ```

5. **Monitor backup health:**
   ```bash
   # Check for recent backups (last 7 days)
   mc find aws/your-backup-bucket/ --newer-than 7d --print

   # Verify backup integrity with checksums
   mc cat aws/your-backup-bucket/postgres/database-2024-01-15.sql.gz | md5sum
   ```

### Backup Verification Checklist

- ✅ Backups are created on schedule
- ✅ Backup files are properly named with timestamps
- ✅ Backup files are not empty (check file sizes)
- ✅ Recent backups exist (within expected time frame)
- ✅ Backup files can be downloaded successfully
- ✅ Backup content is valid (can be opened/restored)
- ✅ Old backups are cleaned up according to retention policy

## Development Setup

### Setting up for Development

1. **Clone and install in development mode:**
   ```bash
   git clone https://github.com/calypr/backup-service.git
   cd backup-service
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Run tests:**
   ```bash
   # Run all tests
   pytest

   # Run with verbose output
   pytest -v

   # Run specific test file
   pytest tests/test_backups.py

   # Run with debug logging
   pytest -v --log-cli-level=DEBUG
   ```

### Code Structure

```
backup-service/
├── src/backup/           # Main package
│   ├── main.py          # CLI entry point
│   ├── options.py       # Click command options
│   ├── postgres/        # PostgreSQL backup logic
│   ├── s3/             # S3 upload/download logic
│   └── grip/           # GRIP database backup logic
├── tests/              # Test suite
├── examples/           # Usage examples
├── Dockerfile          # Container image
└── pyproject.toml      # Package configuration
```

### Testing with Docker

```bash
# Build development image
docker build -t backup-service:dev .

# Run tests in container
docker run --rm backup-service:dev pytest

# Interactive development
docker run -it --rm \
  -v $(pwd):/app \
  backup-service:dev bash
```

## Contributing Guidelines

### Code Style

- Follow **PEP 8** Python style guidelines
- Use **type hints** where possible
- Add **docstrings** for public functions and classes
- Keep functions focused and well-named

### Making Changes

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Ensure all tests pass** before submitting
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

### Testing Requirements

- All new features must include tests
- Tests should use **testcontainers** for integration testing
- Maintain or improve test coverage
- Test both success and failure scenarios

### Pull Request Process

1. Create a descriptive PR title and description
2. Reference any related issues
3. Ensure CI/CD pipelines pass
4. Request review from maintainers
5. Address any feedback promptly

### Release Process

This project uses **semantic-release** for automated versioning and releases:

- Commits follow [Conventional Commits](https://conventionalcommits.org/)
- Releases are automatically created on merge to main
- Docker images are automatically built and published

---

For questions or support, please open an issue in the [GitHub repository](https://github.com/calypr/backup-service/issues).