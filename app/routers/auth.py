


from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.schemas.auth import UserRegister, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import register_user

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

@router.post("/register",response_model=UserResponse,status_code=201)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    user = await register_user(db,user_data)

    if user is None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    return user



    