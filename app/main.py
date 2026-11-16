from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.db.session import engine
from app.routes.auth import router as auth_router
from app.routes.urls import router as urls_router
from redis.asyncio import Redis
from app.core.config import settings
import logging
from socket import gaierror

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )
    logger.info("Starting Linkly API")

    try:
        yield
    finally:
        await app.state.redis.aclose()
        await engine.dispose()
        logger.info("Shutting down Linkly API")



app = FastAPI(
    title="Linkly API",
    description="URL Shortener Backend",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(OperationalError)
@app.exception_handler(gaierror)
async def database_unavailable(_request: Request, _exc: OperationalError | gaierror):
    logger.exception("Database operation failed")
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable"},
    )


app.include_router(auth_router)
app.include_router(urls_router)

@app.get("/")
async def root():
    return {
        "message":"Welcome to Linkly API"
    }


@app.get("/health")
async def health():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, gaierror):
        raise HTTPException(status_code=503, detail="Database unavailable")

    return {
        "status":"healthy"
    }

