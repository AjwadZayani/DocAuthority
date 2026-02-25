# DocAuthority Log / Kafka Local Setup

This folder contains local Kafka bootstrap scripts and a simple Kafka consumer for DocAuthority events.

## What is here

- `start-kafka.sh` - Bash script to start local Kafka and initialize topics
- `kafka-initialise.sh` - Creates DocAuthority Kafka topics (idempotent)
- `consumer.py` - Kafka consumer for DocAuthority topics
- `local_kafka/clean_start.sh` - Temporary clean restart helper (pull fresh image, recreate container, init topics)
- `local_kafka/run_local_kafka.sh` - Temporary smart start helper (reuse existing container if possible)

## Kafka image used

- `confluentinc/confluent-local:latest`

## Temporary local Kafka helpers (pre-compose)

These are temporary helpers until `compose.yaml` is added.

### Start local Kafka (smart start)

```bash
bash backend/log/local_kafka/run_local_kafka.sh
```

Behavior:
- If `local-kafka` exists and is running -> leaves it running
- If `local-kafka` exists but is stopped -> starts it
- If no container exists -> creates one
- If image is missing -> falls back to `clean_start.sh`
- Runs `kafka-initialise.sh`

### Clean restart local Kafka

```bash
bash backend/log/local_kafka/clean_start.sh
```

Behavior:
- Removes existing `local-kafka` container
- Pulls latest Kafka image
- Creates and runs a new `local-kafka` container
- Runs `kafka-initialise.sh`

## Bash flow (existing)

### Start local Kafka + initialize topics

```bash
bash backend/log/start-kafka.sh
```

## Run the consumer

Local Python:

```bash
python backend/log/consumer.py
```

With env overrides:

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 KAFKA_GROUP_ID=docauthority-log-consumer python backend/log/consumer.py
```

## Notes

- Kafka broker default port: `9092`
- Default Kafka container name: `local-kafka`
- `kafka-initialise.sh` creates topics for both `document` and `identity` domains
- `consumer.py` supports JSON event envelope parsing and prints raw payloads when messages are not valid JSON

## TODO (later)

- Add a Kafka UI container in `compose.yaml` for topic inspection, message browsing, and consumer group lag checks.
- Recommended fit: `provectuslabs/kafka-ui`
  - Reason: Docker-friendly, simple setup, works well with local Kafka brokers, useful for topics/messages/consumer groups.
