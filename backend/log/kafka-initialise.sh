#!/bin/bash
set -euo pipefail

# Creates local Kafka topics for DocAuthority domains.
# Supports either:
# 1) local Confluent CLI (`confluent local kafka ...`)
# 2) Docker container started by backend/log/start-kafka.sh (`local-kafka`)

CONTAINER_NAME="${KAFKA_CONTAINER_NAME:-local-kafka}"
BOOTSTRAP_SERVER="${KAFKA_BOOTSTRAP_SERVER:-localhost:9092}"

topic_exists() {
  local topic="$1"
  if command -v confluent >/dev/null 2>&1; then
    confluent local kafka topic list 2>/dev/null | grep -Fxq "$topic"
    return $?
  fi

  docker exec "$CONTAINER_NAME" kafka-topics --bootstrap-server "$BOOTSTRAP_SERVER" --list 2>/dev/null | grep -Fxq "$topic"
}

create_topic() {
  local topic="$1"
  if topic_exists "$topic"; then
    echo "Topic already exists: $topic"
  else
    echo "Creating topic: $topic"
    if command -v confluent >/dev/null 2>&1; then
      confluent local kafka topic create "$topic"
    else
      docker exec "$CONTAINER_NAME" kafka-topics \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --create \
        --if-not-exists \
        --topic "$topic" \
        --partitions 1 \
        --replication-factor 1 >/dev/null
    fi
  fi
}

echo "Initializing DocAuthority Kafka topics..."

# Document domain events (from document service lifecycle and approval flow)
create_topic "docauthority.document.created"
create_topic "docauthority.document.updated"
create_topic "docauthority.document.status.changed"
create_topic "docauthority.document.approval.requested"
create_topic "docauthority.document.approved"
create_topic "docauthority.document.rejected"
create_topic "docauthority.document.published"
create_topic "docauthority.document.archived"
create_topic "docauthority.document.deleted"

# Identity domain events (aligned with current identity endpoints in backend/identity/app/main.py)
create_topic "docauthority.identity.department.created"
create_topic "docauthority.identity.user.registered"
create_topic "docauthority.identity.user.role.assigned"
create_topic "docauthority.identity.auth.login.succeeded"
create_topic "docauthority.identity.role.created"
create_topic "docauthority.identity.role.updated"
create_topic "docauthority.identity.role.deleted"
create_topic "docauthority.identity.permission.created"
create_topic "docauthority.identity.permission.updated"
create_topic "docauthority.identity.permission.deleted"
create_topic "docauthority.identity.role-permission.assigned"
create_topic "docauthority.identity.role-permission.removed"
create_topic "docauthority.identity.role-permission.replaced"

# Cross-service / audit-friendly stream
create_topic "docauthority.audit.events"

# Dead-letter queue for malformed / unprocessable events
create_topic "docauthority.dlq"

echo "Kafka topic initialization complete."
