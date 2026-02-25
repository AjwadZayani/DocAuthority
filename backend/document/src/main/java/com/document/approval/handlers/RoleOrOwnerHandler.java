package com.document.approval.handlers;

import java.util.Set;
import com.document.approval.ApprovalContext;
import com.document.approval.ApprovalResult;
import com.document.approval.BaseApprovalHandler;

public class RoleOrOwnerHandler extends BaseApprovalHandler {
    @Override
    public ApprovalResult handle(ApprovalContext ctx) {
        if (ctx.getActorId().equals(ctx.getDocument().getOwnerId())) {
            return next(ctx);
        }
        Set<String> roles = ctx.getUser().getRoles();
        if (roles.contains("APPROVER")) {
            return next(ctx);
        }
        if (roles.contains("DEPT_APPROVER") && ctx.getUser().getDepartmentId() != null
            && ctx.getUser().getDepartmentId().equals(ctx.getDocument().getDepartmentId())) {
            return next(ctx);
        }
        return ApprovalResult.deny("User not permitted to approve.");
    }
}
