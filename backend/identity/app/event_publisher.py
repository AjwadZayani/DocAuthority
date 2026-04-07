import json
import os
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer


SOURCE = "identity-service"
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
AUDIT_TOPIC = os.getenv("KAFKA_AUDIT_TOPIC", "docauthority.audit.events")

_producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS}) if BOOTSTRAP_SERVERS else None


def _safe_serialize(value):
    if isinstance(value, dict):
        return {k: _safe_serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_safe_serialize(v) for v in value]
    if isinstance(value, tuple):
        return [_safe_serialize(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def build_event(event_type: str, payload: dict, correlation_id=None, actor_id=None):
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "source": SOURCE,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "payload": _safe_serialize(payload),
    }
    if actor_id is not None:
        event["actor_id"] = str(actor_id)
    return event


def publish_event(topic: str, event_type: str, payload: dict, key=None, correlation_id=None, actor_id=None):
    if _producer is None:
        return False
    event = build_event(event_type, payload, correlation_id=correlation_id, actor_id=actor_id)
    try:
        _producer.produce(
            topic,
            key=str(key).encode("utf-8") if key is not None else None,
            value=json.dumps(event, ensure_ascii=True).encode("utf-8"),
        )
        _producer.poll(0)
        return True
    except Exception:
        return False


def publish_audit(event_type: str, payload: dict, key=None, correlation_id=None, actor_id=None):
    return publish_event(
        AUDIT_TOPIC,
        event_type,
        payload,
        key=key,
        correlation_id=correlation_id,
        actor_id=actor_id,
    )


def flush_events(timeout_seconds: float = 2.0):
    if _producer is not None:
        _producer.flush(timeout_seconds)
