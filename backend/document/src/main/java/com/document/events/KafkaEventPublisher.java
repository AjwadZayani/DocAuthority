package com.document.events;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PreDestroy;

@Service
public class KafkaEventPublisher {
    private final ObjectMapper objectMapper;
    private final String source = "document-service";
    private final String auditTopic;
    private final KafkaProducer<String, String> producer;

    public KafkaEventPublisher(
        ObjectMapper objectMapper,
        @Value("${KAFKA_BOOTSTRAP_SERVERS:}") String bootstrapServers,
        @Value("${KAFKA_AUDIT_TOPIC:docauthority.audit.events}") String auditTopic
    ) {
        this.objectMapper = objectMapper;
        this.auditTopic = auditTopic;
        this.producer = createProducer(bootstrapServers);
    }

    private KafkaProducer<String, String> createProducer(String bootstrapServers) {
        if (bootstrapServers == null || bootstrapServers.isBlank()) {
            return null;
        }
        Properties props = new Properties();
        props.put("bootstrap.servers", bootstrapServers);
        props.put("key.serializer", StringSerializer.class.getName());
        props.put("value.serializer", StringSerializer.class.getName());
        props.put("acks", "1");
        return new KafkaProducer<>(props);
    }

    public void publish(String topic, String eventType, String key, Object payload) {
        if (producer == null) {
            return;
        }
        Map<String, Object> envelope = new HashMap<>();
        envelope.put("event_id", UUID.randomUUID().toString());
        envelope.put("event_type", eventType);
        envelope.put("source", source);
        envelope.put("occurred_at", Instant.now().toString());
        envelope.put("correlation_id", null);
        envelope.put("payload", payload);

        try {
            String json = objectMapper.writeValueAsString(envelope);
            producer.send(new ProducerRecord<>(topic, key, json));
        } catch (JsonProcessingException ignored) {
            // Intentionally non-blocking for API requests.
        }
    }

    public void publishAudit(String eventType, String key, Object payload) {
        publish(auditTopic, eventType, key, payload);
    }

    @PreDestroy
    public void close() {
        if (producer != null) {
            producer.flush();
            producer.close();
        }
    }
}
