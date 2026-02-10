package com.document.mapper;

import org.mapstruct.Mapper;
import com.document.dto.DocumentDTO;
import com.document.model.Document;

@Mapper(componentModel = "spring")
public interface DocumentMapper {
    DocumentDTO toDto(Document entity);
    Document toEntity(DocumentDTO dto);
}
