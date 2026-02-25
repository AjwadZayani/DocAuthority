#!/bin/bash

# 1. Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker daemon is not running. Please start Docker first."
    exit 1
fi

# 2. Define container name
CONTAINER_NAME="local-kafka"

# 3. Stop and remove existing container if it exists
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping existing Kafka container..."
    docker rm -f $CONTAINER_NAME >/dev/null
fi

# 4. Start Kafka in KRaft mode
echo "Starting Confluent Kafka (KRaft mode) on port 9092..."
docker run -d \
  --name $CONTAINER_NAME \
  -p 9092:9092 \
  confluentinc/confluent-local:latest

# 5. Wait for Kafka to be ready
echo "Waiting for Kafka to initialize..."
sleep 5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INIT_SCRIPT="$SCRIPT_DIR/kafka-initialise.sh"

if [ -f "$INIT_SCRIPT" ]; then
    echo "Initializing Kafka topics..."
    bash "$INIT_SCRIPT"
else
    echo "Warning: kafka-initialise.sh not found. Skipping topic initialization."
fi

echo "Kafka is now running at localhost:9092"
echo "You can now use your 'confluent-kafka' Python library to connect."
