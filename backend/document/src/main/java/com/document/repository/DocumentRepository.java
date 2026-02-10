package com.document.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.document.model.Document;
import java.util.UUID;

public interface DocumentRepository extends JpaRepository<Document, UUID> {
    // Add custom query methods here if needed
}
