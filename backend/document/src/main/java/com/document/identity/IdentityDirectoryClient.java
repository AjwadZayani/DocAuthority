package com.document.identity;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class IdentityDirectoryClient {
    private final RestClient restClient;
    private final String internalToken;

    public IdentityDirectoryClient(
        @Value("${identity.service.base-url:http://localhost:5001}") String baseUrl,
        @Value("${identity.service.internal-token:}") String internalToken
    ) {
        this.restClient = RestClient.builder().baseUrl(baseUrl).build();
        this.internalToken = internalToken;
    }

    public DirectoryRecord getUser(UUID userId) {
        if (userId == null || internalToken == null || internalToken.isBlank()) {
            return null;
        }

        try {
            return restClient.get()
                .uri("/internal/users/{id}", userId)
                .header("X-Internal-Token", internalToken)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(DirectoryRecord.class);
        } catch (Exception ignored) {
            return null;
        }
    }

    public DepartmentRecord getDepartment(UUID departmentId) {
        if (departmentId == null || internalToken == null || internalToken.isBlank()) {
            return null;
        }

        try {
            return restClient.get()
                .uri("/internal/departments/{id}", departmentId)
                .header("X-Internal-Token", internalToken)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(DepartmentRecord.class);
        } catch (Exception ignored) {
            return null;
        }
    }

    public List<DirectoryRecord> getUsers(List<UUID> userIds) {
        if (userIds == null || userIds.isEmpty() || internalToken == null || internalToken.isBlank()) {
            return Collections.emptyList();
        }

        try {
            return restClient.post()
                .uri("/internal/users/bulk")
                .header("X-Internal-Token", internalToken)
                .accept(MediaType.APPLICATION_JSON)
                .contentType(MediaType.APPLICATION_JSON)
                .body(Map.of("user_ids", userIds))
                .retrieve()
                .body(new org.springframework.core.ParameterizedTypeReference<List<DirectoryRecord>>() {});
        } catch (Exception ignored) {
            return Collections.emptyList();
        }
    }

    public List<DepartmentRecord> getDepartments(List<UUID> departmentIds) {
        if (departmentIds == null || departmentIds.isEmpty() || internalToken == null || internalToken.isBlank()) {
            return Collections.emptyList();
        }

        try {
            return restClient.post()
                .uri("/internal/departments/bulk")
                .header("X-Internal-Token", internalToken)
                .accept(MediaType.APPLICATION_JSON)
                .contentType(MediaType.APPLICATION_JSON)
                .body(Map.of("department_ids", departmentIds))
                .retrieve()
                .body(new org.springframework.core.ParameterizedTypeReference<List<DepartmentRecord>>() {});
        } catch (Exception ignored) {
            return Collections.emptyList();
        }
    }
}
