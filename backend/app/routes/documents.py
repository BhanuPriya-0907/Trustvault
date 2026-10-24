
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.permission import Permission

from app.services.document_service import (
    create_document_record,
    get_user_documents,
)
from app.services.token_service import verify_access_token
from app.schemas.document import DocumentCreate
from app.utils.file_validator import (
    validate_file_extension,
    validate_file_size,
)


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/documents", tags=["Documents"])
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


def check_document_access(
    document: Document,
    current_user: User,
    db: Session,
    require_edit: bool = False,
) -> None:
    if document.owner_id == current_user.id:
        return

    permission = (
        db.query(Permission)
        .filter(
            Permission.document_id == document.id,
            Permission.user_id == current_user.id,
        )
        .first()
    )

    if permission is None or not permission.can_read:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this document",
        )

    if require_edit and not permission.can_edit:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to edit this document",
        )


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


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    check_document_access(document, current_user, db)

    # Resolve the storage path and ensure it stays inside UPLOAD_DIR.
    upload_root = UPLOAD_DIR.resolve()
    file_path = (upload_root / document.storage_key).resolve()

    if file_path.parent != upload_root:
        raise HTTPException(
            status_code=400,
            detail="Invalid document storage path",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stored document file not found",
        )

    return FileResponse(
        path=file_path,
        filename=document.name,
        media_type="application/octet-stream",
    )


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

    storage_key = (
        f"{uuid.uuid4().hex}{Path(file.filename).suffix.lower()}"
    )
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

    except Exception as exc:
        file_path.unlink(missing_ok=True)
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not save the uploaded document",
        ) from exc

    finally:
        file.file.close()
