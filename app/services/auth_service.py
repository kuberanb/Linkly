
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.session import get_db
from app.schemas.auth import UserRegister
from app.models import User

from app.core.security import (
    decode_access_token,
    hash_password,
    verify_password,
    create_access_token
)

async def register_user(db:AsyncSession,user_data:UserRegister):
    email = user_data.email.lower()

    result = await db.execute(
        select(User).where(
            User.email == email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        return None

    new_user = User(
        name=user_data.name,
        email=email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return None

    await db.refresh(new_user)

    return new_user


async def login_user(db:AsyncSession,email:str,password:str):

    result = await db.execute(
        select(User).where(User.email == email.lower())
    )

    db_user : User = result.scalar_one_or_none()

    if not db_user:
        return None

    if not verify_password(
        password,
        db_user.hashed_password
    ):
        return None

    if not db_user.is_active:
        return None

    access_token = create_access_token(user_id=str(db_user.id))

    return {
        "access_token":access_token,
        "token_type":"bearer"
    }

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(db :AsyncSession = Depends(get_db), credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> User:

    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise auth_error

    try:

        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])

    except (InvalidTokenError, KeyError, ValueError, TypeError):
       raise auth_error

    result = await db.execute(Select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise auth_error

    return user
