package com.document.controller;

import java.util.HashMap;
import org.springframework.web.bind.annotation.RestController;
import com.document.service.DocumentService;
import com.document.dto.DocumentDTO;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static java.util.stream.Collectors.toList;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.server.ResponseStatusException;

import com.document.model.Document;
import com.document.mapper.DocumentMapper;
import com.document.events.KafkaEventPublisher;

@RestController
@RequestMapping("/documents")
public class DocumentController {
    private DocumentService svc;
    private DocumentMapper mapper;
    private KafkaEventPublisher eventPublisher;

    DocumentController(DocumentService svc, DocumentMapper mapper, KafkaEventPublisher eventPublisher) {
        this.svc = svc;
        this.mapper = mapper;
        this.eventPublisher = eventPublisher;
    }

    private Map<String, Object> documentPayload(Document doc) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("document_id", doc.getId() != null ? doc.getId().toString() : null);
        payload.put("status", doc.getStatus() != null ? doc.getStatus().name() : null);
        payload.put("sensitivity", doc.getSensitivity() != null ? doc.getSensitivity().name() : null);
        payload.put("owner_id", doc.getOwnerId() != null ? doc.getOwnerId().toString() : null);
        payload.put("department_id", doc.getDepartmentId() != null ? doc.getDepartmentId().toString() : null);
        return payload;
    }

    private void publishDocumentEvent(String topic, String eventType, Document doc) {
        String key = doc.getId() != null ? doc.getId().toString() : null;
        eventPublisher.publish(topic, eventType, key, documentPayload(doc));
        eventPublisher.publishAudit(eventType, key, documentPayload(doc));
    }

    @GetMapping
    public List<DocumentDTO> getDocuments() {
        return svc.getDocuments().stream().map(mapper::toDto).collect(toList());
    }

    @PostMapping
    public DocumentDTO createDocument(@RequestBody DocumentDTO dto) {
        Document doc = mapper.toEntity(dto);
        doc.setId(null);
        doc.setVersion(null);
        Document savedDoc = svc.saveDocument(doc);
        publishDocumentEvent("docauthority.document.created", "docauthority.document.created", savedDoc);
        return mapper.toDto(savedDoc);
    }

    @DeleteMapping("/{id}")
    public void deleteDocument(@PathVariable UUID id) {
        Document existing = svc.findDocumentById(id);
        if (existing == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Document not found with id " + id);
        } else {
            svc.deleteDocument(id);
            Map<String, Object> payload = new HashMap<>();
            payload.put("document_id", id.toString());
            eventPublisher.publish("docauthority.document.deleted", "docauthority.document.deleted", id.toString(), payload);
            eventPublisher.publishAudit("docauthority.document.deleted", id.toString(), payload);
        }
    }

    @PatchMapping("/{id}")
    public DocumentDTO updateDocument(@PathVariable UUID id, @RequestBody DocumentDTO dto) {
        Document existingDoc = svc.findDocumentById(id);
        if (existingDoc == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Document not found with id " + id);
        }
        if (dto.getName() != null) {
            existingDoc.setName(dto.getName());
        }
        if (dto.getContent() != null) {
            existingDoc.setContent(dto.getContent());
        }
        if (dto.getOwnerId() != null) {
            existingDoc.setOwnerId(dto.getOwnerId());
        }
        if (dto.getDepartmentId() != null) {
            existingDoc.setDepartmentId(dto.getDepartmentId());
        }
        if (dto.getStatus() != null) {
            existingDoc.setStatus(dto.getStatus());
        }
        if (dto.getSensitivity() != null) {
            existingDoc.setSensitivity(dto.getSensitivity());
        }
        if (dto.getRejectionReason() != null) {
            existingDoc.setRejectionReason(dto.getRejectionReason());
        }
        if (dto.getPublishedAt() != null) {
            existingDoc.setPublishedAt(dto.getPublishedAt());
        }
        if (dto.getArchivedAt() != null) {
            existingDoc.setArchivedAt(dto.getArchivedAt());
        }
        if (dto.getDeletedAt() != null) {
            existingDoc.setDeletedAt(dto.getDeletedAt());
        }
        Document updatedDoc = svc.saveDocument(existingDoc);
        publishDocumentEvent("docauthority.document.updated", "docauthority.document.updated", updatedDoc);
        return mapper.toDto(updatedDoc);
    }

    @PatchMapping("/{id}/status")
    public DocumentDTO updateStatus(@PathVariable UUID id, @RequestBody DocumentDTO dto) {
        if (dto.getStatus() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "status is required");
        }
        Document existingDoc = svc.findDocumentById(id);
        if (existingDoc == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Document not found with id " + id);
        }
        existingDoc.setStatus(dto.getStatus());
        Document saved = svc.saveDocument(existingDoc);
        publishDocumentEvent("docauthority.document.status.changed", "docauthority.document.status.changed", saved);
        return mapper.toDto(saved);
    }

    @PatchMapping("/{id}/sensitivity")
    public DocumentDTO updateSensitivity(@PathVariable UUID id, @RequestBody DocumentDTO dto) {
        if (dto.getSensitivity() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "sensitivity is required");
        }
        Document existingDoc = svc.findDocumentById(id);
        if (existingDoc == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Document not found with id " + id);
        }
        existingDoc.setSensitivity(dto.getSensitivity());
        Document saved = svc.saveDocument(existingDoc);
        publishDocumentEvent("docauthority.document.updated", "docauthority.document.updated", saved);
        return mapper.toDto(saved);
    }

    @PatchMapping("/{id}/rejection-reason")
    public DocumentDTO updateRejectionReason(@PathVariable UUID id, @RequestBody DocumentDTO dto) {
        if (dto.getRejectionReason() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "rejectionReason is required");
        }
        Document existingDoc = svc.findDocumentById(id);
        if (existingDoc == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Document not found with id " + id);
        }
        existingDoc.setRejectionReason(dto.getRejectionReason());
        Document saved = svc.saveDocument(existingDoc);
        publishDocumentEvent("docauthority.document.rejected", "docauthority.document.rejected", saved);
        return mapper.toDto(saved);
    }

    @PatchMapping("/{id}/published-at")
    public DocumentDTO updatePublishedAt(@PathVariable UUID id, @RequestBody DocumentDTO dto) {
        if (dto.getPublishedAt() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "publishedAt is required");
        }
        Document existingDoc = svc.findDocumentById(id);
        if (existingDoc == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Document not found with id " + id);
        }
        existingDoc.setPublishedAt(dto.getPublishedAt());
        Document saved = svc.saveDocument(existingDoc);
        publishDocumentEvent("docauthority.document.published", "docauthority.document.published", saved);
        return mapper.toDto(saved);
    }

    @PatchMapping("/{id}/archived-at")
    public DocumentDTO updateArchivedAt(@PathVariable UUID id, @RequestBody DocumentDTO dto) {
        if (dto.getArchivedAt() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "archivedAt is required");
        }
        Document existingDoc = svc.findDocumentById(id);
        if (existingDoc == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Document not found with id " + id);
        }
        existingDoc.setArchivedAt(dto.getArchivedAt());
        Document saved = svc.saveDocument(existingDoc);
        publishDocumentEvent("docauthority.document.archived", "docauthority.document.archived", saved);
        return mapper.toDto(saved);
    }

    @PatchMapping("/{id}/deleted-at")
    public DocumentDTO updateDeletedAt(@PathVariable UUID id, @RequestBody DocumentDTO dto) {
        if (dto.getDeletedAt() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "deletedAt is required");
        }
        Document existingDoc = svc.findDocumentById(id);
        if (existingDoc == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Document not found with id " + id);
        }
        existingDoc.setDeletedAt(dto.getDeletedAt());
        Document saved = svc.saveDocument(existingDoc);
        publishDocumentEvent("docauthority.document.deleted", "docauthority.document.deleted", saved);
        return mapper.toDto(saved);
    }

    @PostMapping("/{id}/approve")
    public void approveDocument(@PathVariable UUID id, @RequestParam UUID actorId) {
        var result = svc.approveDocument(id, actorId);
        if (!result.isAllowed()) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, result.getReason());
        }
        Document approved = svc.findDocumentById(id);
        if (approved != null) {
            publishDocumentEvent("docauthority.document.approved", "docauthority.document.approved", approved);
        }
    }
    
    
    
}
