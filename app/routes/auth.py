


from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from app.schemas.auth import UserRegister, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import register_user, login_user

from app.schemas.auth import UserLogin, Token

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


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    token = await login_user(db, user_data.email, user_data.password)

    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return token



    
