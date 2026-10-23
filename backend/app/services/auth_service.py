
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.security import hash_password


def register_user(
    db: Session,
    user_data: UserCreate,
) -> User:
    existing_user = (
        db.query(User)
        .filter(
            (User.email == user_data.email)
            | (User.username == user_data.username)
        )
        .first()
    )

    if existing_user:
        raise ValueError("Email or username already registered")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="viewer",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
