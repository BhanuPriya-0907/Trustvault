
import uuid

from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate


def create_document_record(
    db: Session,
    document_data: DocumentCreate,
    owner_id: int,
    storage_key: str | None = None,
) -> Document:
    document = Document(
        name=document_data.name,
        category=document_data.category,
        owner_id=owner_id,
        storage_key=storage_key or str(uuid.uuid4()),
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_user_documents(
    db: Session,
    owner_id: int,
) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.owner_id == owner_id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document_by_id(
    db: Session,
    document_id: int,
) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )
