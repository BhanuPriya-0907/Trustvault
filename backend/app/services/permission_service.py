
from sqlalchemy.orm import Session

from app.models.permission import Permission


def grant_permission(
    db: Session,
    document_id: int,
    user_id: int,
    granted_by: int,
    can_read: bool = False,
    can_edit: bool = False,
    can_delete: bool = False,
) -> Permission:
    permission = (
        db.query(Permission)
        .filter(
            Permission.document_id == document_id,
            Permission.user_id == user_id,
        )
        .first()
    )

    if permission is None:
        permission = Permission(
            document_id=document_id,
            user_id=user_id,
            granted_by=granted_by,
        )
        db.add(permission)

    permission.can_read = can_read
    permission.can_edit = can_edit
    permission.can_delete = can_delete
    permission.granted_by = granted_by

    db.commit()
    db.refresh(permission)

    return permission


def revoke_permission(
    db: Session,
    document_id: int,
    user_id: int,
) -> bool:
    permission = (
        db.query(Permission)
        .filter(
            Permission.document_id == document_id,
            Permission.user_id == user_id,
        )
        .first()
    )

    if permission is None:
        return False

    db.delete(permission)
    db.commit()

    return True
