package com.document.approval;

public abstract class BaseApprovalHandler implements ApprovalHandler {
    private ApprovalHandler next;

    @Override
    public void setNext(ApprovalHandler next) {
        this.next = next;
    }

    protected ApprovalResult next(ApprovalContext ctx) {
        return next == null ? ApprovalResult.allow() : next.handle(ctx);
    }
}
