from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine
from app.routes.auth import router as auth_router
from app.routes.urls import router as urls_router


@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Starting Linkly API")

    yield

    await engine.dispose()

    print("Shutting down Linkly")



app = FastAPI(
    title="Linkly API",
    description="URL Shortener Backend",
    version="1.0.0",
    lifespan=lifespan
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
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")

    return {
        "status":"healthy"
    }

