from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import httpx
import time

from database import engine, Base
from routers import auth, notebooks, sources, chat
from config import settings
from middleware import RateLimitMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="DevLog API",
    description="Backend for DevLog — AI knowledge base for developers",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

app.include_router(auth.router,      prefix="/api/auth",      tags=["auth"])
app.include_router(notebooks.router, prefix="/api/notebooks", tags=["notebooks"])
app.include_router(sources.router,   prefix="/api/sources",   tags=["sources"])
app.include_router(chat.router,      prefix="/api/chat",      tags=["chat"])

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.time()}
