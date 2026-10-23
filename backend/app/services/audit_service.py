
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record_audit_event(
    db: Session,
    action: str,
    user_id: int | None = None,
    document_id: int | None = None,
    details: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    event = AuditLog(
        user_id=user_id,
        document_id=document_id,
        action=action,
        details=details,
        ip_address=ip_address,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_recent_audit_events(
    db: Session,
    limit: int = 100,
) -> list[AuditLog]:
    safe_limit = max(1, min(limit, 500))

    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(safe_limit)
        .all()
    )
