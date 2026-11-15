from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import engine
from app.routes.auth import router as auth_router


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

@app.get("/")
async def root():
    return {
        "message":"Welcome to Linkly API"
    }


@app.get("/helath")
async def health():
    return {
        "status":"healthy"
    }

