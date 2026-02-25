package com.document.approval;

public interface ApprovalHandler {
    ApprovalResult handle(ApprovalContext ctx);
    void setNext(ApprovalHandler next);
}
