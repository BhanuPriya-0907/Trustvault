import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.utils.file_validator import (
    validate_file_extension,
    validate_file_size,
)


import os
from pathlib import Path


from app.database import get_db
from app.models.user import User
from app.models.document import Document

from app.services.document_service import (
    create_document_record,
    get_user_documents,
)
from app.schemas.document import DocumentCreate
from app.services.token_service import verify_access_token


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = verify_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.get("/health")
def documents_health():
    return {"message": "Document routes are ready"}


@router.get("/")
def list_my_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = get_user_documents(db, current_user.id)

    return [
        {
            "id": document.id,
            "name": document.name,
            "category": document.category,
            "owner_id": document.owner_id,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
        }
        for document in documents
    ]

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    category: str = Form("General"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail="File type is not allowed",
        )

    contents = file.file.read()

    if not validate_file_size(len(contents)):
        raise HTTPException(
            status_code=400,
            detail="File size must be 10 MB or less",
        )

    storage_key = f"{uuid.uuid4().hex}{Path(file.filename).suffix.lower()}"
    file_path = UPLOAD_DIR / storage_key

    try:
        with file_path.open("wb") as saved_file:
            saved_file.write(contents)

        document_data = DocumentCreate(
            name=Path(file.filename).name,
            category=category,
        )

        document = create_document_record(
            db=db,
            document_data=document_data,
            owner_id=current_user.id,
            storage_key=storage_key,
        )

        return {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "name": document.name,
            "category": document.category,
        }

    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Could not save the uploaded document",
        )
    finally:
        file.file.close()

