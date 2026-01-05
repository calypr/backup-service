# Creating a custom Docker image to include the s3 snapshot repository plugin
# Ref: https://github.com/elastic/helm-charts/blob/v7.17.3/elasticsearch/README.md#how-to-install-plugins

# Manual build command:
# docker buildx build --platform=linux/arm64,linux/amd64 -t quay.io/ohsu-comp-bio/elasticsearch-s3:7.17.3 -f Dockerfile.es . --push
# TODO: Add this to GitHub Actions for automatic builds

# Start from the official Elasticsearch image you are currently using
FROM docker.elastic.co/elasticsearch/elasticsearch:7.17.3

# Install the S3 repository plugin
# The 'install' command runs at build time, and is baked into the final image
RUN bin/elasticsearch-plugin install --batch repository-s3
