package com.document.approval.handlers;

import com.document.approval.ApprovalContext;
import com.document.approval.ApprovalResult;
import com.document.approval.BaseApprovalHandler;

public class SensitivityHandler extends BaseApprovalHandler {
    @Override
    public ApprovalResult handle(ApprovalContext ctx) {
        if (!ctx.getUser().getClearance().contains(ctx.getDocument().getSensitivity())) {
            return ApprovalResult.deny("Insufficient clearance.");
        }
        return next(ctx);
    }
}
