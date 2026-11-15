

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse
from app.services.auth_service import get_current_user
from app.services.cache_service import get_cached_url, cache_url
from app.services.url_service import create_short_url
from datetime import datetime, timezone

from fastapi.responses import RedirectResponse
from sqlalchemy import or_, select, update

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
    request: Request,
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    redis_client = request.app.state.redis
    original_url = await get_cached_url(redis_client, short_code)
    link = None

    if original_url is None:
        result = await db.execute(
            select(URL).where(URL.short_code == short_code)
        )
        link = result.scalar_one_or_none()
        if link is None:
            raise HTTPException(status_code=404, detail="Short URL not found")
        original_url = link.original_url

    result = await db.execute(
        update(URL)
        .where(
            URL.short_code == short_code,
            URL.is_active.is_(True),
            or_(
                URL.expires_at.is_(None),
                URL.expires_at > datetime.now(timezone.utc),
            ),
        )
        .values(click_count=URL.click_count + 1)
    )
    if result.rowcount != 1:
        await db.rollback()
        raise HTTPException(status_code=404, detail="Short URL not found")

    await db.commit()

    if link is not None and link.expires_at is None:
        await cache_url(redis_client, short_code, original_url)

    return RedirectResponse(url=original_url, status_code=302)



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
