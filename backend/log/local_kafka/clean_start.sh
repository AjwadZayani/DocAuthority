#!/bin/bash
set -euo pipefail

# Temporary local Kafka bootstrap helper (pre-compose).
# Wipes the existing local-kafka container, pulls latest image, recreates it,
# then runs topic initialization.

CONTAINER_NAME="${KAFKA_CONTAINER_NAME:-local-kafka}"
IMAGE_NAME="${KAFKA_IMAGE_NAME:-confluentinc/confluent-local:latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INIT_SCRIPT="$LOG_DIR/kafka-initialise.sh"

echo "[1/5] Checking Docker daemon..."
if ! docker info >/dev/null 2>&1; then
  echo "Error: Docker daemon is not running. Start Docker first."
  exit 1
fi

echo "[2/5] Removing existing container if present..."
if docker ps -aq -f "name=^${CONTAINER_NAME}$" | grep -q .; then
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

echo "[3/5] Pulling latest Kafka image..."
docker pull "$IMAGE_NAME"

echo "[4/5] Starting Kafka container..."
docker run -d --name "$CONTAINER_NAME" -p 9092:9092 "$IMAGE_NAME" >/dev/null

echo "[5/5] Waiting for Kafka, then initializing topics..."
sleep 5

if [[ -f "$INIT_SCRIPT" ]]; then
  bash "$INIT_SCRIPT"
else
  echo "Warning: kafka-initialise.sh not found at $INIT_SCRIPT"
fi

echo "Kafka is running at localhost:9092"
