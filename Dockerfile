FROM python:slim

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

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client

ENTRYPOINT ["./entrypoint.sh"]
