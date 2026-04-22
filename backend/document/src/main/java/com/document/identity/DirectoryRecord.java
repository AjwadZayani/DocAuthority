package com.document.identity;

public record DirectoryRecord(
    String id,
    String name,
    String email,
    String department_id,
    String department_name
) {}
