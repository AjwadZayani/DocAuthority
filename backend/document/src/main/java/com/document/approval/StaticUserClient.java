package com.document.approval;

import java.util.Set;
import java.util.UUID;
import org.springframework.stereotype.Service;
import com.document.enums.SENSITIVITY;

@Service
public class StaticUserClient implements UserClient {
    @Override
    public UserSnapshot getUser(UUID userId) {
        Set<String> roles = Set.of();
        Set<SENSITIVITY> clearance = Set.of(SENSITIVITY.PUBLIC, SENSITIVITY.INTERNAL);
        return new UserSnapshot(userId, null, roles, clearance);
    }
}
