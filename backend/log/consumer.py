#!/usr/bin/env python

import json
import os
from datetime import datetime, timezone
from confluent_kafka import Consumer, Producer


DEFAULT_TOPICS = [
    "docauthority.document.created",
    "docauthority.document.updated",
    "docauthority.document.status.changed",
    "docauthority.document.approved",
    "docauthority.document.rejected",
    "docauthority.identity.user.registered",
    "docauthority.identity.auth.login.succeeded",
    "docauthority.audit.events",
]

REQUIRED_EVENT_FIELDS = [
    "event_id",
    "event_type",
    "source",
    "occurred_at",
    "payload",
]


def _decode(value):
    if value is None:
        return None
    try:
        return value.decode("utf-8")
    except Exception:
        return str(value)


def _parse_event(raw_value):
    try:
        event = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": f"Invalid JSON: {exc}",
            "event": None,
        }

    if not isinstance(event, dict):
        return {
            "ok": False,
            "error": "Event payload must be a JSON object",
            "event": None,
        }

    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        return {
            "ok": False,
            "error": f"Missing required event fields: {', '.join(missing)}",
            "event": event,
        }

    return {"ok": True, "error": None, "event": event}


def _build_dlq_event(msg, raw_value, parse_error):
    return {
        "error_type": "invalid_event_envelope",
        "error_message": parse_error,
        "original_topic": msg.topic(),
        "original_partition": msg.partition(),
        "original_offset": msg.offset(),
        "received_at": datetime.now(timezone.utc).isoformat(),
        "raw_value": raw_value,
    }


def _publish_dlq(producer, dlq_topic, msg, raw_value, parse_error):
    try:
        dlq_payload = _build_dlq_event(msg, raw_value, parse_error)
        producer.produce(
            dlq_topic,
            key=(msg.key() if msg.key() is not None else None),
            value=json.dumps(dlq_payload, ensure_ascii=True).encode("utf-8"),
        )
        producer.poll(0)
        return True
    except Exception as exc:
        print(f"[DLQ-ERROR] topic={msg.topic()} offset={msg.offset()} error={exc}")
        return False


if __name__ == '__main__':
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    group_id = os.getenv("KAFKA_GROUP_ID", "docauthority-log-consumer")
    dlq_topic = os.getenv("KAFKA_DLQ_TOPIC", "docauthority.dlq")
    topics_env = os.getenv("KAFKA_TOPICS")
    topics = [t.strip() for t in topics_env.split(",")] if topics_env else DEFAULT_TOPICS

    config = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
    }

    consumer = Consumer(config)
    producer = Producer({"bootstrap.servers": bootstrap_servers})
    consumer.subscribe(topics)

    print(f"Subscribed to topics: {', '.join(topics)}")
    print(f"Bootstrap server: {bootstrap_servers}")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"ERROR: {msg.error()}")
                continue

            key = _decode(msg.key())
            value = _decode(msg.value())
            metadata = (
                f"topic={msg.topic()} partition={msg.partition()} "
                f"offset={msg.offset()} key={key}"
            )

            parsed = _parse_event(value) if isinstance(value, str) else {
                "ok": False,
                "error": "Message value is not decodable text",
                "event": None,
            }

            if not parsed["ok"]:
                _publish_dlq(producer, dlq_topic, msg, value, parsed["error"])
                # Keep non-JSON events visible during local development.
                print(f"[RAW] {metadata} parse_error={parsed['error']} value={value}")
                continue

            event = parsed["event"]
            print(
                "[EVENT] "
                f"{metadata} "
                f"event_type={event.get('event_type')} "
                f"source={event.get('source')} "
                f"occurred_at={event.get('occurred_at')} "
                f"event_id={event.get('event_id')} "
                f"correlation_id={event.get('correlation_id')}"
            )
            print(f"        payload={json.dumps(event.get('payload'), ensure_ascii=True)}")
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush(5)
        consumer.close()
