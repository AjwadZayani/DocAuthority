package com.document.approval;

import java.util.UUID;

public interface UserClient {
    UserSnapshot getUser(UUID userId);
}
