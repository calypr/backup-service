# Backup build
FROM python:slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  gcc \
  libpq-dev \ 
  postgresql-client

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
