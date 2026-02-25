package com.document.approval;

import java.util.UUID;
import com.document.model.Document;

public class ApprovalContext {
    private final UUID documentId;
    private final UUID actorId;
    private final Document document;
    private final UserSnapshot user;

    public ApprovalContext(UUID documentId, UUID actorId, Document document, UserSnapshot user) {
        this.documentId = documentId;
        this.actorId = actorId;
        this.document = document;
        this.user = user;
    }

    public UUID getDocumentId() {
        return documentId;
    }

    public UUID getActorId() {
        return actorId;
    }

    public Document getDocument() {
        return document;
    }

    public UserSnapshot getUser() {
        return user;
    }
}
