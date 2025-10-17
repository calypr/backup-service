# Backup build
FROM python:slim

# Note: Installing Postgres 14 for now to match the versions used by Gen3-Helm
#
# Gen3-Helm Chart
# https://github.com/uc-cdis/gen3-helm/blob/gen3-0.2.69/helm/gen3/Chart.yaml#L143-L146
#
# Bitnami PostgreSQL 11.9.13 (14.5.0):
# https://github.com/bitnami/charts/blob/c6076945ecc47791d82e545a20ef690dd93ff662/bitnami/postgresql/Chart.yaml#L4
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  gcc \
  libpq-dev \ 
  postgresql-client-14

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
