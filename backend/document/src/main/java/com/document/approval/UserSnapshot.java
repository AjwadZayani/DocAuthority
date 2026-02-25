package com.document.approval;

import java.util.Set;
import java.util.UUID;
import com.document.enums.SENSITIVITY;

public class UserSnapshot {
    private final UUID id;
    private final UUID departmentId;
    private final Set<String> roles;
    private final Set<SENSITIVITY> clearance;

    public UserSnapshot(UUID id, UUID departmentId, Set<String> roles, Set<SENSITIVITY> clearance) {
        this.id = id;
        this.departmentId = departmentId;
        this.roles = roles;
        this.clearance = clearance;
    }

    public UUID getId() {
        return id;
    }

    public UUID getDepartmentId() {
        return departmentId;
    }

    public Set<String> getRoles() {
        return roles;
    }

    public Set<SENSITIVITY> getClearance() {
        return clearance;
    }
}
