package com.document.mapper;

import com.document.dto.DocumentDTO;
import com.document.model.Document;
import javax.annotation.processing.Generated;
import org.springframework.stereotype.Component;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2026-01-28T14:22:59+0800",
    comments = "version: 1.6.3, compiler: javac, environment: Java 21.0.6 (Eclipse Adoptium)"
)
@Component
public class DocumentMapperImpl implements DocumentMapper {

    @Override
    public DocumentDTO toDto(Document entity) {
        if ( entity == null ) {
            return null;
        }

        DocumentDTO documentDTO = new DocumentDTO();

        documentDTO.setId( entity.getId() );
        documentDTO.setName( entity.getName() );
        documentDTO.setContent( entity.getContent() );
        documentDTO.setOwnerId( entity.getOwnerId() );
        documentDTO.setDepartmentId( entity.getDepartmentId() );
        documentDTO.setStatus( entity.getStatus() );
        documentDTO.setSensitivity( entity.getSensitivity() );
        if ( entity.getVersion() != null ) {
            documentDTO.setVersion( entity.getVersion().doubleValue() );
        }
        documentDTO.setRejectionReason( entity.getRejectionReason() );
        documentDTO.setPublishedAt( entity.getPublishedAt() );
        documentDTO.setArchivedAt( entity.getArchivedAt() );
        documentDTO.setDeletedAt( entity.getDeletedAt() );
        documentDTO.setCreatedAt( entity.getCreatedAt() );
        documentDTO.setUpdatedAt( entity.getUpdatedAt() );

        return documentDTO;
    }

    @Override
    public Document toEntity(DocumentDTO dto) {
        if ( dto == null ) {
            return null;
        }

        Document document = new Document();

        document.setId( dto.getId() );
        document.setName( dto.getName() );
        document.setContent( dto.getContent() );
        document.setOwnerId( dto.getOwnerId() );
        document.setDepartmentId( dto.getDepartmentId() );
        document.setStatus( dto.getStatus() );
        document.setSensitivity( dto.getSensitivity() );
        if ( dto.getVersion() != null ) {
            document.setVersion( dto.getVersion().longValue() );
        }
        document.setRejectionReason( dto.getRejectionReason() );
        document.setPublishedAt( dto.getPublishedAt() );
        document.setArchivedAt( dto.getArchivedAt() );
        document.setDeletedAt( dto.getDeletedAt() );
        document.setCreatedAt( dto.getCreatedAt() );
        document.setUpdatedAt( dto.getUpdatedAt() );

        return document;
    }
}
