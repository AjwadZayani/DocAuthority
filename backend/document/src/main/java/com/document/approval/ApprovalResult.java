package com.document.approval;

public class ApprovalResult {
    private final boolean allowed;
    private final String reason;

    private ApprovalResult(boolean allowed, String reason) {
        this.allowed = allowed;
        this.reason = reason;
    }

    public static ApprovalResult allow() {
        return new ApprovalResult(true, null);
    }

    public static ApprovalResult deny(String reason) {
        return new ApprovalResult(false, reason);
    }

    public boolean isAllowed() {
        return allowed;
    }

    public String getReason() {
        return reason;
    }
}
