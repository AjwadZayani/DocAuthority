#!/bin/bash
set -euo pipefail

# Temporary local Kafka startup helper (pre-compose).
# Reuses existing local-kafka container when possible; falls back to clean_start.

CONTAINER_NAME="${KAFKA_CONTAINER_NAME:-local-kafka}"
IMAGE_NAME="${KAFKA_IMAGE_NAME:-confluentinc/confluent-local:latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INIT_SCRIPT="$LOG_DIR/kafka-initialise.sh"
CLEAN_START_SCRIPT="$SCRIPT_DIR/clean_start.sh"

echo "[1/4] Checking Docker daemon..."
if ! docker info >/dev/null 2>&1; then
  echo "Error: Docker daemon is not running. Start Docker first."
  exit 1
fi

echo "[2/4] Checking for existing Kafka container..."
if docker ps -aq -f "name=^${CONTAINER_NAME}$" | grep -q .; then
  if [[ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER_NAME")" == "true" ]]; then
    echo "Kafka container is already running: $CONTAINER_NAME"
    exit 0
  fi

  echo "Starting existing Kafka container..."
  docker start "$CONTAINER_NAME" >/dev/null
  sleep 5
  if [[ -f "$INIT_SCRIPT" ]]; then
    bash "$INIT_SCRIPT"
  fi
  echo "Kafka is running at localhost:9092"
  exit 0
fi

echo "[3/4] No container found. Checking local image..."
if ! docker images -q "$IMAGE_NAME" | grep -q .; then
  echo "Kafka image not found locally. Running clean start..."
  bash "$CLEAN_START_SCRIPT"
  exit 0
fi

echo "[4/4] Creating Kafka container from local image..."
docker run -d --name "$CONTAINER_NAME" -p 9092:9092 "$IMAGE_NAME" >/dev/null
sleep 5
if [[ -f "$INIT_SCRIPT" ]]; then
  bash "$INIT_SCRIPT"
fi
echo "Kafka is running at localhost:9092"
