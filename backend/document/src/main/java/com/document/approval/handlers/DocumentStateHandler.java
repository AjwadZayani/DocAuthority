package com.document.approval.handlers;

import com.document.approval.ApprovalContext;
import com.document.approval.ApprovalResult;
import com.document.approval.BaseApprovalHandler;
import com.document.enums.STATUS;

public class DocumentStateHandler extends BaseApprovalHandler {
    @Override
    public ApprovalResult handle(ApprovalContext ctx) {
        if (ctx.getDocument().getStatus() != STATUS.IN_REVIEW) {
            return ApprovalResult.deny("Document not in review.");
        }
        return next(ctx);
    }
}
