
import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret_key() -> str:
    secret_key = os.getenv("TRUSTVAULT_SECRET_KEY")

    if not secret_key or len(secret_key) < 32:
        raise RuntimeError(
            "Set TRUSTVAULT_SECRET_KEY to a secret of at least 32 characters."
        )

    return secret_key


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        get_secret_key(),
        algorithm=ALGORITHM,
    )


def verify_access_token(token: str) -> int:
    payload = jwt.decode(
        token,
        get_secret_key(),
        algorithms=[ALGORITHM],
    )

    user_id = payload.get("sub")

    if not isinstance(user_id, str) or not user_id.isdigit():
        raise InvalidTokenError("Invalid user ID in token")

    return int(user_id)
