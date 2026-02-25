package com.document.service;

import java.util.List;

import org.springframework.stereotype.Service;

import java.util.UUID;
import com.document.approval.ApprovalContext;
import com.document.approval.ApprovalHandler;
import com.document.approval.ApprovalResult;
import com.document.approval.UserClient;
import com.document.approval.UserSnapshot;
import com.document.approval.handlers.DocumentStateHandler;
import com.document.approval.handlers.RoleOrOwnerHandler;
import com.document.approval.handlers.SensitivityHandler;
import com.document.model.Document;
import com.document.enums.STATUS;
import com.document.repository.DocumentRepository;

@Service
public class DocumentService {
    DocumentRepository repo;
    UserClient userClient;

    DocumentService(DocumentRepository repo, UserClient userClient) {
        this.repo = repo;
        this.userClient = userClient;
    }

    public <Optional>List<Document> getDocuments() {
        return repo.findAll();
    }

    public Document saveDocument(Document doc) {
        return repo.save(doc);
    }

    public Document findDocumentById(UUID id) {
        return repo.findById(id).orElse(null);
    }

    public void deleteDocument(UUID id) {
        repo.deleteById(id);
    }

    public ApprovalResult approveDocument(UUID docId, UUID actorId) {
        Document doc = repo.findById(docId).orElse(null);
        if (doc == null) {
            return ApprovalResult.deny("Document not found.");
        }
        UserSnapshot user = userClient.getUser(actorId);

        ApprovalHandler state = new DocumentStateHandler();
        ApprovalHandler role = new RoleOrOwnerHandler();
        ApprovalHandler sensitivity = new SensitivityHandler();
        state.setNext(role);
        role.setNext(sensitivity);

        ApprovalContext ctx = new ApprovalContext(docId, actorId, doc, user);
        ApprovalResult result = state.handle(ctx);
        if (!result.isAllowed()) {
            return result;
        }

        doc.setStatus(STATUS.APPROVED);
        repo.save(doc);
        return ApprovalResult.allow();
    }


}
