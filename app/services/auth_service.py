
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import UserRegister
from app.models import User

from app.core.security import (
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

    await db.commit()

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

