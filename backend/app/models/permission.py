
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "user_id",
            name="unique_document_user_permission",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    can_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    can_edit: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    can_delete: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    granted_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
