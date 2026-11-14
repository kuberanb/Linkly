
from argon2 import hash_password
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import UserRegister
from app.models import User

async def register_user(db:AsyncSession,user_data:UserRegister):

    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        return None

    new_user = User(
        email= user_data.email,
        password_hash= hash_password(user_data.password)
    )

    db.add(new_user)

    await db.commit()

    await db.refresh(new_user)

    return new_user

