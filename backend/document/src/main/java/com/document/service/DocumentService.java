package com.document.service;

import java.util.List;

import org.springframework.stereotype.Service;

import java.util.UUID;
import com.document.model.Document;
import com.document.repository.DocumentRepository;

@Service
public class DocumentService {
    DocumentRepository repo;

    DocumentService(DocumentRepository repo) {
        this.repo = repo;
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


}
