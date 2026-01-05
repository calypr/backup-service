# Backup build
FROM python:slim

RUN apt-get update && apt-get install -y \
  build-essential \
  gcc \
  libpq-dev 

RUN apt-get install -y postgresql-common

RUN YES=true /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

# Note: We're using Postgres 14 to match the version set in Gen3-Helm:
#
# Gen3-Helm Chart: https://github.com/calypr/gen3-helm/blob/v1.0.0/helm/gen3/Chart.yaml#L92-L94
#
# Postgres Chart: https://github.com/bitnami/charts/blob/postgresql/11.9.13/bitnami/postgresql/Chart.yaml#L4
#
# ```
# ➜ kubectl exec --stdin --tty StatefulSets/cbds-postgresql -- /bin/bash
# $ psql --version
# psql (PostgreSQL) 14.5
# ```
RUN apt-get update && apt-get install -y postgresql-client-14

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY pyproject.toml .
COPY src ./src

RUN pip install -e .

# Local directory for storing backups before uploading to S3
RUN mkdir -p /backups

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
