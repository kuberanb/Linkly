

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse
from app.services.auth_service import get_current_user
from app.services.url_service import create_short_url
from datetime import datetime, timezone

from fastapi.responses import RedirectResponse
from sqlalchemy import select, update

from app.models.url import URL

router = APIRouter(
    prefix="/api/urls", tags=["URLs"]
)

@router.post("",response_model=URLResponse,status_code=201)
async def create_url(
    data:URLCreate,
    db : AsyncSession =  Depends(get_db),
    current_user : User = Depends(get_current_user)

) :
    link = await create_short_url(db,current_user.id,str(data.original_url))

    if link is None:
        raise HTTPException(status_code=503,detail="Could not create Short URL")

    return link


@router.get("/{short_code}")
async def open_short_url(
    short_code:str,
    db:AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )

    link = result.scalar_one_or_none()

    if link is None or not link.is_active:
        raise HTTPException(status_code=404, detail= "Short URL not found")

    if link.expires_at and link.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail= "Short URL not found")

    await db.execute(
        update(URL)
        .where(URL.id == link.id)
        .values(click_count=URL.click_count + 1)
    )
    await db.commit()

    return RedirectResponse(url=link.original_url,status_code=302)



@router.get("", response_model=list[URLResponse])
async def list_my_urls(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    result = await db.execute(
        select(URL)
        .where(URL.user_id == current_user.id)
        .order_by(URL.created_at.desc(), URL.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()