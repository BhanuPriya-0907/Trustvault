
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.permission import Permission
from app.services.token_service import verify_access_token
from app.services.audit_service import record_audit_event

router = APIRouter(prefix="/permissions", tags=["Permissions"])
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    try:
        user_id = verify_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user


class ShareRequest(BaseModel):
    document_id: int
    email: EmailStr
    can_edit: bool = False


@router.get("/health")
def permissions_health():
    return {"message": "Permission routes are ready"}


@router.post("/share")
def share_document(
    request: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == request.document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the document owner can share this document",
        )

    recipient = (
        db.query(User)
        .filter(User.email == str(request.email))
        .first()
    )

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Recipient user not found",
        )

    if recipient.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot share a document with yourself",
        )

    permission = (
        db.query(Permission)
        .filter(
            Permission.document_id == document.id,
            Permission.user_id == recipient.id,
        )
        .first()
    )

    if permission is None:
        permission = Permission(
            document_id=document.id,
            user_id=recipient.id,
            can_read=True,
            can_edit=request.can_edit,
            can_delete=False,
            granted_by=current_user.id,
        )
        db.add(permission)
    else:
        permission.can_read = True
        permission.can_edit = request.can_edit
        permission.can_delete = False
        permission.granted_by = current_user.id

    db.commit()

    record_audit_event(
        db=db,
        action="DOCUMENT_SHARED",
        user_id=current_user.id,
        document_id=document.id,
        details=(
            f"Shared with {recipient.email}; "
            f"can_edit={request.can_edit}"
        ),
    )

    return {
        "message": "Document shared successfully",
        "document_id": document.id,
        "shared_with": recipient.email,
        "can_read": True,
        "can_edit": request.can_edit,
    }
