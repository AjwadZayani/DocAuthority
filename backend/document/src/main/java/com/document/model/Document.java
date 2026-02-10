package com.document.model;

import java.time.Instant;
import java.util.UUID;
import com.document.enums.STATUS;
import com.document.enums.SENSITIVITY;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Version;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

@Entity
public class Document {
    private @Id 
    @GeneratedValue UUID id;    
    @Column(nullable = false, length = 200)
    private String name;
    @Lob
    @Column(nullable = false)
    private String content;
    @Column(nullable = false)
    private UUID ownerId;
    @Column(nullable = false)
    private UUID departmentId;
    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private STATUS status;
    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private SENSITIVITY sensitivity;
    @Version
    private Long version;
    @Column(nullable = true, length = 500)
    private String rejectionReason;
    @Column(nullable = true)
    private Instant publishedAt;
    @Column(nullable = true)
    private Instant archivedAt;
    @Column(nullable = true)
    private Instant deletedAt;
    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private Instant createdAt;
    @UpdateTimestamp
    @Column(nullable = false)
    private Instant updatedAt;

    public Document() {}

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public UUID getOwnerId() {
        return ownerId;
    }

    public void setOwnerId(UUID ownerId) {
        this.ownerId = ownerId;
    }

    public UUID getDepartmentId() {
        return departmentId;
    }

    public void setDepartmentId(UUID departmentId) {
        this.departmentId = departmentId;
    }

    public STATUS getStatus() {
        return status;
    }

    public void setStatus(STATUS status) {
        this.status = status;
    }

    public SENSITIVITY getSensitivity() {
        return sensitivity;
    }

    public void setSensitivity(SENSITIVITY sensitivity) {
        this.sensitivity = sensitivity;
    }

    public Long getVersion() {
        return version;
    }

    public void setVersion(Long version) {
        this.version = version;
    }

    public String getRejectionReason() {
        return rejectionReason;
    }

    public void setRejectionReason(String rejectionReason) {
        this.rejectionReason = rejectionReason;
    }

    public Instant getPublishedAt() {
        return publishedAt;
    }

    public void setPublishedAt(Instant publishedAt) {
        this.publishedAt = publishedAt;
    }

    public Instant getArchivedAt() {
        return archivedAt;
    }

    public void setArchivedAt(Instant archivedAt) {
        this.archivedAt = archivedAt;
    }

    public Instant getDeletedAt() {
        return deletedAt;
    }

    public void setDeletedAt(Instant deletedAt) {
        this.deletedAt = deletedAt;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
