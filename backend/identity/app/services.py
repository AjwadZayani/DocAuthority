import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash

from database import Base, SessionLocal, engine
from event_publisher import publish_audit, publish_event
from models import Department, Role, Sensitivity, User


JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


def init_db():
    Base.metadata.create_all(bind=engine)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"ok": True, "status": 200, "error": None, "data": payload}
    except jwt.ExpiredSignatureError:
        return {"ok": False, "status": 401, "error": "Token expired", "data": None}
    except jwt.InvalidTokenError:
        return {"ok": False, "status": 401, "error": "Invalid token", "data": None}


def _serialize_user(user: User):
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "department_id": str(user.department_id),
        "is_active": user.is_active,
        "roles": [role.name for role in user.roles],
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
    }


def _create_access_token(user_id: str):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _max_sensitivity_for_user(user: User):
    if any(role.is_root_admin for role in user.roles):
        return Sensitivity.RESTRICTED

    rank = {
        Sensitivity.PUBLIC: 0,
        Sensitivity.INTERNAL: 1,
        Sensitivity.CONFIDENTIAL: 2,
        Sensitivity.RESTRICTED: 3,
    }
    best = Sensitivity.PUBLIC
    for role in user.roles:
        for perm in role.permissions:
            if rank[perm.min_sensitivity] > rank[best]:
                best = perm.min_sensitivity
    return best


def _expand_clearance(max_sensitivity: Sensitivity):
    ordered = [
        Sensitivity.PUBLIC,
        Sensitivity.INTERNAL,
        Sensitivity.CONFIDENTIAL,
        Sensitivity.RESTRICTED,
    ]
    idx = ordered.index(max_sensitivity)
    return [s.value for s in ordered[: idx + 1]]


def _upsert_permission(session, name: str, description: str, level: Sensitivity):
    from models import Permission

    permission = session.query(Permission).filter(Permission.name == name).first()
    if permission is None:
        permission = Permission(name=name, description=description, min_sensitivity=level)
        session.add(permission)
        session.flush()
    else:
        permission.description = description
        permission.min_sensitivity = level
    return permission


def _upsert_role(session, name: str, description: str, level: int, is_root_admin: bool):
    role = session.query(Role).filter(Role.name == name).first()
    if role is None:
        role = Role(name=name, description=description, level=level, is_root_admin=is_root_admin)
        session.add(role)
        session.flush()
    else:
        role.description = description
        role.level = level
        role.is_root_admin = is_root_admin
    return role


def seed_identity_data():
    session = SessionLocal()
    try:
        p_public = _upsert_permission(
            session,
            "DOC_APPROVE_PUBLIC",
            "Approve PUBLIC documents",
            Sensitivity.PUBLIC,
        )
        p_internal = _upsert_permission(
            session,
            "DOC_APPROVE_INTERNAL",
            "Approve INTERNAL documents",
            Sensitivity.INTERNAL,
        )
        p_confidential = _upsert_permission(
            session,
            "DOC_APPROVE_CONFIDENTIAL",
            "Approve CONFIDENTIAL documents",
            Sensitivity.CONFIDENTIAL,
        )
        p_restricted = _upsert_permission(
            session,
            "DOC_APPROVE_RESTRICTED",
            "Approve RESTRICTED documents",
            Sensitivity.RESTRICTED,
        )

        r_public = _upsert_role(
            session,
            "DOC_APPROVER_PUBLIC",
            "Can approve PUBLIC docs",
            10,
            False,
        )
        r_internal = _upsert_role(
            session,
            "DOC_APPROVER_INTERNAL",
            "Can approve up to INTERNAL docs",
            20,
            False,
        )
        r_confidential = _upsert_role(
            session,
            "DOC_APPROVER_CONFIDENTIAL",
            "Can approve up to CONFIDENTIAL docs",
            30,
            False,
        )
        r_restricted = _upsert_role(
            session,
            "DOC_APPROVER_RESTRICTED",
            "Can approve up to RESTRICTED docs",
            40,
            False,
        )
        r_root = _upsert_role(
            session,
            "ROOT_ADMIN",
            "IT root administrator role",
            100,
            True,
        )

        r_public.permissions = [p_public]
        r_internal.permissions = [p_public, p_internal]
        r_confidential.permissions = [p_public, p_internal, p_confidential]
        r_restricted.permissions = [p_public, p_internal, p_confidential, p_restricted]
        r_root.permissions = [p_public, p_internal, p_confidential, p_restricted]

        r_internal.parent_role = r_public
        r_confidential.parent_role = r_internal
        r_restricted.parent_role = r_confidential
        r_root.parent_role = r_restricted

        root_email = os.getenv("ROOT_ADMIN_EMAIL")
        root_password = os.getenv("ROOT_ADMIN_PASSWORD")
        root_name = os.getenv("ROOT_ADMIN_NAME", "IT Root Admin")
        root_dept_name = os.getenv("ROOT_ADMIN_DEPARTMENT", "IT")
        root_created = False

        if root_email and root_password:
            department = session.query(Department).filter(Department.name == root_dept_name).first()
            if department is None:
                department = Department(name=root_dept_name, description="IT Department")
                session.add(department)
                session.flush()

            root_user = session.query(User).filter(User.email == root_email.lower().strip()).first()
            if root_user is None:
                root_user = User(
                    name=root_name,
                    email=root_email.lower().strip(),
                    password_hash=generate_password_hash(root_password),
                    department_id=department.id,
                    is_active=True,
                )
                session.add(root_user)
                session.flush()
                root_created = True

            if r_root not in root_user.roles:
                root_user.roles.append(r_root)

        session.commit()
        publish_audit(
            "docauthority.identity.seed.completed",
            {
                "permissions_seeded": 4,
                "roles_seeded": 5,
                "root_admin_created": root_created,
            },
        )
        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "permissions_seeded": 4,
                "roles_seeded": 5,
                "root_admin_created": root_created,
            },
        }
    finally:
        session.close()

def add_user_role(user_id: str, role_name: str | None = None, role_id: str | None = None):
    session = SessionLocal()
    try:
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid user id", "data": None}

        user = session.query(User).filter(User.id == user_uuid).first()
        if user is None:
            return {"ok": False, "status": 404, "error": "User not found", "data": None}

        role = None
        if role_id:
            try:
                role_uuid = UUID(role_id)
            except ValueError:
                return {"ok": False, "status": 400, "error": "Invalid role id", "data": None}
            role = session.get(Role, role_uuid)
        elif role_name:
            role = session.query(Role).filter(Role.name == role_name).first()
        else:
            return {"ok": False, "status": 400, "error": "role_name or role_id is required", "data": None}

        if role is None:
            return {"ok": False, "status": 404, "error": "Role not found", "data": None}

        if role not in user.roles:
            user.roles.append(role)
            session.commit()
            publish_event(
                "docauthority.identity.user.role.assigned",
                "docauthority.identity.user.role.assigned",
                {
                    "user_id": str(user.id),
                    "role_id": str(role.id),
                    "role_name": role.name,
                },
                key=user.id,
                actor_id=user.id,
            )

        return {"ok": True, "status": 200, "error": None, "data": _serialize_user(user)}
    finally:
        session.close()

def register_user(name: str, email: str, password: str, department_id: str, roles: list[str] | None = None):
    session = SessionLocal()
    try:
        try:
            department_uuid = UUID(department_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid department_id", "data": None}

        department = session.get(Department, department_uuid)
        if department is None:
            return {"ok": False, "status": 404, "error": "Department not found", "data": None}

        user = User(
            name=name,
            email=email.lower().strip(),
            password_hash=generate_password_hash(password),
            roles=roles or [],
            department_id=department.id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        publish_event(
            "docauthority.identity.user.registered",
            "docauthority.identity.user.registered",
            {"user_id": str(user.id), "email": user.email, "department_id": str(user.department_id)},
            key=user.id,
            actor_id=user.id,
        )
        return {"ok": True, "status": 201, "error": None, "data": _serialize_user(user)}
    except IntegrityError:
        session.rollback()
        return {"ok": False, "status": 409, "error": "Email already exists", "data": None}
    finally:
        session.close()


def create_department(name: str, description: str | None = None):
    session = SessionLocal()
    try:
        department = Department(
            name=name.strip(),
            description=description.strip() if isinstance(description, str) else None,
        )
        session.add(department)
        session.commit()
        session.refresh(department)
        publish_event(
            "docauthority.identity.department.created",
            "docauthority.identity.department.created",
            {"department_id": str(department.id), "name": department.name},
            key=department.id,
        )
        return {
            "ok": True,
            "status": 201,
            "error": None,
            "data": {
                "id": str(department.id),
                "name": department.name,
                "description": department.description,
                "created_at": department.created_at.isoformat() if department.created_at else None,
            },
        }
    except IntegrityError:
        session.rollback()
        return {
            "ok": False,
            "status": 409,
            "error": "Department already exists",
            "data": None,
        }
    finally:
        session.close()


def _parse_sensitivity(value: str):
    try:
        return Sensitivity[value.strip().upper()]
    except Exception:
        return None


def create_role(
    name: str,
    description: str | None = None,
    level: int = 0,
    is_root_admin: bool = False,
    parent_role_id: str | None = None,
):
    session = SessionLocal()
    try:
        parent_id = None
        if parent_role_id:
            try:
                parent_id = UUID(parent_role_id)
            except ValueError:
                return {"ok": False, "status": 400, "error": "Invalid parent_role_id", "data": None}

            parent = session.get(Role, parent_id)
            if parent is None:
                return {"ok": False, "status": 404, "error": "Parent role not found", "data": None}

        role = Role(
            name=name.strip(),
            description=description.strip() if isinstance(description, str) else None,
            level=int(level),
            is_root_admin=bool(is_root_admin),
            parent_role_id=parent_id,
        )
        session.add(role)
        session.commit()
        session.refresh(role)
        publish_event(
            "docauthority.identity.role.created",
            "docauthority.identity.role.created",
            {
                "role_id": str(role.id),
                "name": role.name,
                "level": role.level,
                "is_root_admin": role.is_root_admin,
                "parent_role_id": str(role.parent_role_id) if role.parent_role_id else None,
            },
            key=role.id,
        )
        return {
            "ok": True,
            "status": 201,
            "error": None,
            "data": {
                "id": str(role.id),
                "name": role.name,
                "description": role.description,
                "level": role.level,
                "is_root_admin": role.is_root_admin,
                "parent_role_id": str(role.parent_role_id) if role.parent_role_id else None,
            },
        }
    except IntegrityError:
        session.rollback()
        return {"ok": False, "status": 409, "error": "Role already exists", "data": None}
    finally:
        session.close()


def update_role(role_id: str, payload: dict):
    session = SessionLocal()
    try:
        try:
            role_uuid = UUID(role_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid role id", "data": None}

        role = session.get(Role, role_uuid)
        if role is None:
            return {"ok": False, "status": 404, "error": "Role not found", "data": None}

        if "name" in payload and payload["name"]:
            role.name = str(payload["name"]).strip()
        if "description" in payload:
            role.description = str(payload["description"]).strip() if payload["description"] else None
        if "level" in payload and payload["level"] is not None:
            role.level = int(payload["level"])
        if "is_root_admin" in payload and payload["is_root_admin"] is not None:
            role.is_root_admin = bool(payload["is_root_admin"])
        if "parent_role_id" in payload:
            parent_role_id = payload["parent_role_id"]
            if parent_role_id:
                try:
                    parent_uuid = UUID(parent_role_id)
                except ValueError:
                    return {"ok": False, "status": 400, "error": "Invalid parent_role_id", "data": None}
                parent = session.get(Role, parent_uuid)
                if parent is None:
                    return {"ok": False, "status": 404, "error": "Parent role not found", "data": None}
                role.parent_role_id = parent_uuid
            else:
                role.parent_role_id = None

        session.commit()
        session.refresh(role)
        publish_event(
            "docauthority.identity.role.updated",
            "docauthority.identity.role.updated",
            {
                "role_id": str(role.id),
                "name": role.name,
                "level": role.level,
                "is_root_admin": role.is_root_admin,
                "parent_role_id": str(role.parent_role_id) if role.parent_role_id else None,
            },
            key=role.id,
        )
        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "id": str(role.id),
                "name": role.name,
                "description": role.description,
                "level": role.level,
                "is_root_admin": role.is_root_admin,
                "parent_role_id": str(role.parent_role_id) if role.parent_role_id else None,
            },
        }
    except IntegrityError:
        session.rollback()
        return {"ok": False, "status": 409, "error": "Role update conflict", "data": None}
    finally:
        session.close()


def delete_role(role_id: str):
    session = SessionLocal()
    try:
        try:
            role_uuid = UUID(role_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid role id", "data": None}

        role = session.get(Role, role_uuid)
        if role is None:
            return {"ok": False, "status": 404, "error": "Role not found", "data": None}

        role.permissions = []
        role.users = []
        role.parent_role_id = None
        for child in role.child_roles:
            child.parent_role_id = None
        deleted_role_id = str(role.id)
        deleted_role_name = role.name
        session.delete(role)
        session.commit()
        publish_event(
            "docauthority.identity.role.deleted",
            "docauthority.identity.role.deleted",
            {"role_id": deleted_role_id, "name": deleted_role_name},
            key=deleted_role_id,
        )
        return {"ok": True, "status": 200, "error": None, "data": {"deleted": True}}
    finally:
        session.close()


def create_permission(name: str, description: str | None, min_sensitivity: str):
    session = SessionLocal()
    try:
        level = _parse_sensitivity(min_sensitivity)
        if level is None:
            return {"ok": False, "status": 400, "error": "Invalid min_sensitivity", "data": None}

        from models import Permission

        permission = Permission(
            name=name.strip(),
            description=description.strip() if isinstance(description, str) else None,
            min_sensitivity=level,
        )
        session.add(permission)
        session.commit()
        session.refresh(permission)
        publish_event(
            "docauthority.identity.permission.created",
            "docauthority.identity.permission.created",
            {
                "permission_id": str(permission.id),
                "name": permission.name,
                "min_sensitivity": permission.min_sensitivity.value,
            },
            key=permission.id,
        )
        return {
            "ok": True,
            "status": 201,
            "error": None,
            "data": {
                "id": str(permission.id),
                "name": permission.name,
                "description": permission.description,
                "min_sensitivity": permission.min_sensitivity.value,
            },
        }
    except IntegrityError:
        session.rollback()
        return {"ok": False, "status": 409, "error": "Permission already exists", "data": None}
    finally:
        session.close()


def update_permission(permission_id: str, payload: dict):
    session = SessionLocal()
    try:
        from models import Permission

        try:
            perm_uuid = UUID(permission_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid permission id", "data": None}

        permission = session.get(Permission, perm_uuid)
        if permission is None:
            return {"ok": False, "status": 404, "error": "Permission not found", "data": None}

        if "name" in payload and payload["name"]:
            permission.name = str(payload["name"]).strip()
        if "description" in payload:
            permission.description = str(payload["description"]).strip() if payload["description"] else None
        if "min_sensitivity" in payload and payload["min_sensitivity"]:
            level = _parse_sensitivity(payload["min_sensitivity"])
            if level is None:
                return {"ok": False, "status": 400, "error": "Invalid min_sensitivity", "data": None}
            permission.min_sensitivity = level

        session.commit()
        session.refresh(permission)
        publish_event(
            "docauthority.identity.permission.updated",
            "docauthority.identity.permission.updated",
            {
                "permission_id": str(permission.id),
                "name": permission.name,
                "min_sensitivity": permission.min_sensitivity.value,
            },
            key=permission.id,
        )
        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "id": str(permission.id),
                "name": permission.name,
                "description": permission.description,
                "min_sensitivity": permission.min_sensitivity.value,
            },
        }
    except IntegrityError:
        session.rollback()
        return {"ok": False, "status": 409, "error": "Permission update conflict", "data": None}
    finally:
        session.close()


def delete_permission(permission_id: str):
    session = SessionLocal()
    try:
        from models import Permission

        try:
            perm_uuid = UUID(permission_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid permission id", "data": None}

        permission = session.get(Permission, perm_uuid)
        if permission is None:
            return {"ok": False, "status": 404, "error": "Permission not found", "data": None}

        deleted_permission_id = str(permission.id)
        deleted_permission_name = permission.name
        permission.roles = []
        session.delete(permission)
        session.commit()
        publish_event(
            "docauthority.identity.permission.deleted",
            "docauthority.identity.permission.deleted",
            {"permission_id": deleted_permission_id, "name": deleted_permission_name},
            key=deleted_permission_id,
        )
        return {"ok": True, "status": 200, "error": None, "data": {"deleted": True}}
    finally:
        session.close()


def assign_permission_to_role(role_id: str, permission_id: str):
    session = SessionLocal()
    try:
        from models import Permission

        try:
            role_uuid = UUID(role_id)
            permission_uuid = UUID(permission_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid role_id or permission_id", "data": None}

        role = session.get(Role, role_uuid)
        permission = session.get(Permission, permission_uuid)
        if role is None:
            return {"ok": False, "status": 404, "error": "Role not found", "data": None}
        if permission is None:
            return {"ok": False, "status": 404, "error": "Permission not found", "data": None}

        if permission not in role.permissions:
            role.permissions.append(permission)
            session.commit()
            publish_event(
                "docauthority.identity.role-permission.assigned",
                "docauthority.identity.role-permission.assigned",
                {"role_id": str(role.id), "permission_id": str(permission.id)},
                key=role.id,
            )

        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "role_id": str(role.id),
                "permission_id": str(permission.id),
                "assigned": True,
            },
        }
    finally:
        session.close()


def remove_permission_from_role(role_id: str, permission_id: str):
    session = SessionLocal()
    try:
        from models import Permission

        try:
            role_uuid = UUID(role_id)
            permission_uuid = UUID(permission_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid role_id or permission_id", "data": None}

        role = session.get(Role, role_uuid)
        permission = session.get(Permission, permission_uuid)
        if role is None:
            return {"ok": False, "status": 404, "error": "Role not found", "data": None}
        if permission is None:
            return {"ok": False, "status": 404, "error": "Permission not found", "data": None}

        if permission in role.permissions:
            role.permissions.remove(permission)
            session.commit()
            publish_event(
                "docauthority.identity.role-permission.removed",
                "docauthority.identity.role-permission.removed",
                {"role_id": str(role.id), "permission_id": str(permission.id)},
                key=role.id,
            )

        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "role_id": str(role.id),
                "permission_id": str(permission.id),
                "removed": True,
            },
        }
    finally:
        session.close()


def replace_role_permission(role_id: str, old_permission_id: str, new_permission_id: str):
    session = SessionLocal()
    try:
        from models import Permission

        try:
            role_uuid = UUID(role_id)
            old_uuid = UUID(old_permission_id)
            new_uuid = UUID(new_permission_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid role or permission ids", "data": None}

        role = session.get(Role, role_uuid)
        old_permission = session.get(Permission, old_uuid)
        new_permission = session.get(Permission, new_uuid)
        if role is None:
            return {"ok": False, "status": 404, "error": "Role not found", "data": None}
        if old_permission is None or new_permission is None:
            return {"ok": False, "status": 404, "error": "Permission not found", "data": None}

        if old_permission in role.permissions:
            role.permissions.remove(old_permission)
        if new_permission not in role.permissions:
            role.permissions.append(new_permission)
        session.commit()
        publish_event(
            "docauthority.identity.role-permission.replaced",
            "docauthority.identity.role-permission.replaced",
            {
                "role_id": str(role.id),
                "old_permission_id": str(old_permission.id),
                "new_permission_id": str(new_permission.id),
            },
            key=role.id,
        )
        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "role_id": str(role.id),
                "old_permission_id": str(old_permission.id),
                "new_permission_id": str(new_permission.id),
                "updated": True,
            },
        }
    finally:
        session.close()


def login_user(email: str, password: str):
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .filter(User.email == email.lower().strip())
            .first()
        )
        if user is None or not check_password_hash(user.password_hash, password):
            return {"ok": False, "status": 401, "error": "Invalid credentials", "data": None}
        if not user.is_active:
            return {"ok": False, "status": 403, "error": "User is inactive", "data": None}

        user.last_login_at = datetime.utcnow()
        session.commit()

        token = _create_access_token(str(user.id))
        publish_event(
            "docauthority.identity.auth.login.succeeded",
            "docauthority.identity.auth.login.succeeded",
            {"user_id": str(user.id), "email": user.email},
            key=user.id,
            actor_id=user.id,
        )
        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user": _serialize_user(user),
            },
        }
    finally:
        session.close()


def get_user(user_id: str):
    session = SessionLocal()
    try:
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid user id", "data": None}

        user = (
            session.query(User)
            .options(joinedload(User.roles), joinedload(User.department))
            .filter(User.id == user_uuid)
            .first()
        )
        if user is None:
            return {"ok": False, "status": 404, "error": "User not found", "data": None}
        payload = _serialize_user(user)
        payload["department_name"] = user.department.name if user.department else None
        return {"ok": True, "status": 200, "error": None, "data": payload}
    finally:
        session.close()


def get_user_directory(user_id: str):
    session = SessionLocal()
    try:
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid user id", "data": None}

        user = (
            session.query(User)
            .options(joinedload(User.department))
            .filter(User.id == user_uuid)
            .first()
        )
        if user is None:
            return {"ok": False, "status": 404, "error": "User not found", "data": None}

        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "department_id": str(user.department_id),
                "department_name": user.department.name if user.department else None,
            },
        }
    finally:
        session.close()


def get_user_directories(user_ids: list[str]):
    session = SessionLocal()
    try:
        user_uuids = []
        seen = set()

        for user_id in user_ids:
            try:
                user_uuid = UUID(str(user_id))
            except ValueError:
                continue

            if user_uuid in seen:
                continue

            seen.add(user_uuid)
            user_uuids.append(user_uuid)

        if not user_uuids:
            return {"ok": True, "status": 200, "error": None, "data": []}

        users = (
            session.query(User)
            .options(joinedload(User.department))
            .filter(User.id.in_(user_uuids))
            .all()
        )

        payload = [
            {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "department_id": str(user.department_id),
                "department_name": user.department.name if user.department else None,
            }
            for user in users
        ]

        return {"ok": True, "status": 200, "error": None, "data": payload}
    finally:
        session.close()


def get_department(department_id: str):
    session = SessionLocal()
    try:
        try:
            department_uuid = UUID(department_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid department id", "data": None}

        department = session.get(Department, department_uuid)
        if department is None:
            return {"ok": False, "status": 404, "error": "Department not found", "data": None}

        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": {
                "id": str(department.id),
                "name": department.name,
                "description": department.description,
                "created_at": department.created_at.isoformat() if department.created_at else None,
            },
        }
    finally:
        session.close()


def get_departments(department_ids: list[str]):
    session = SessionLocal()
    try:
        department_uuids = []
        seen = set()

        for department_id in department_ids:
            try:
                department_uuid = UUID(str(department_id))
            except ValueError:
                continue

            if department_uuid in seen:
                continue

            seen.add(department_uuid)
            department_uuids.append(department_uuid)

        if not department_uuids:
            return {"ok": True, "status": 200, "error": None, "data": []}

        departments = session.query(Department).filter(Department.id.in_(department_uuids)).all()
        payload = [
            {
                "id": str(department.id),
                "name": department.name,
                "description": department.description,
                "created_at": department.created_at.isoformat() if department.created_at else None,
            }
            for department in departments
        ]

        return {"ok": True, "status": 200, "error": None, "data": payload}
    finally:
        session.close()


def get_user_snapshot(user_id: str):
    session = SessionLocal()
    try:
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid user id", "data": None}

        user = (
            session.query(User)
            .options(joinedload(User.roles).joinedload(Role.permissions))
            .filter(User.id == user_uuid)
            .first()
        )
        if user is None:
            return {"ok": False, "status": 404, "error": "User not found", "data": None}

        max_sensitivity = _max_sensitivity_for_user(user)
        clearance = _expand_clearance(max_sensitivity)
        roles = [role.name for role in user.roles]
        payload = {
            "id": str(user.id),
            "department_id": str(user.department_id),
            "roles": roles,
            "clearance": clearance,
            "is_root_admin": any(role.is_root_admin for role in user.roles),
        }
        return {"ok": True, "status": 200, "error": None, "data": payload}
    finally:
        session.close()


def is_root_admin_user(user_id: str):
    session = SessionLocal()
    try:
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return {"ok": False, "status": 400, "error": "Invalid user id", "data": None}
        user = (
            session.query(User)
            .options(joinedload(User.roles))
            .filter(User.id == user_uuid)
            .first()
        )
        if user is None:
            return {"ok": False, "status": 404, "error": "User not found", "data": None}
        return {
            "ok": True,
            "status": 200,
            "error": None,
            "data": any(role.is_root_admin for role in user.roles),
        }
    finally:
        session.close()
