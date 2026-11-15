
from secrets import token_urlsafe
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL


async def create_short_url(db: AsyncSession,user_id: UUID,original_url : str ) -> URL | None :

    for _ in range(3):
        
        link = URL(
            user_id=user_id,
            original_url=original_url,
            short_code=token_urlsafe(12),
        )

        db.add(link)

        try:
            await db.commit()
        except IntegrityError :
            await db.rollback()
            continue

        await db.refresh(link)

        return link

    return None
