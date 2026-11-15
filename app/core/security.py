

from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings


# Password hashing instance using Argon2
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_id: str) -> str:
    """Generate a JWT access token."""

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""

    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
        options={"require": ["exp", "sub"]}
    )

    return payload
