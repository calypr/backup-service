# GRIP build
# Ref: https://github.com/bmeg/grip/blob/develop/Dockerfile
FROM golang:1.17.2-alpine AS grip

RUN apk add --no-cache make git bash build-base

ENV GOPATH=/go
ENV PATH="/go/bin:${PATH}"

WORKDIR /go/src/github.com/bmeg

RUN git clone https://github.com/bmeg/grip

WORKDIR /go/src/github.com/bmeg/grip

# Checkout latest GRIP tag. Example:
# $ git describe --tags --abbrev=0
# v1.9.0
RUN git checkout $(git describe --tags --abbrev=0)

RUN make install

# Backup build
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

# Copy GRIP binary from build stage
COPY --from=grip /go/bin/grip /usr/local/bin/grip

ENTRYPOINT ["./entrypoint.sh"]
