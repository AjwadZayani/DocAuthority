package com.document.mapper;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import com.document.dto.DocumentDTO;
import com.document.model.Document;

@Mapper(componentModel = "spring")
public interface DocumentMapper {
    @Mapping(target = "ownerName", ignore = true)
    @Mapping(target = "departmentName", ignore = true)
    DocumentDTO toDto(Document entity);
    Document toEntity(DocumentDTO dto);
}
