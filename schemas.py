from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ── Auth ─────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username may only contain letters, numbers, hyphens and underscores")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Notebooks ────────────────────────────────────────────────────────
class NotebookCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    category: Optional[str] = "Backend"


class NotebookUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_shared: Optional[bool] = None


class NotebookOut(BaseModel):
    id: str
    name: str
    description: str
    category: str
    is_shared: bool
    source_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Sources ──────────────────────────────────────────────────────────
class SourceCreate(BaseModel):
    name: str
    source_type: str = "file"   # file | url | github | npm | api_docs | paste
    content: Optional[str] = ""
    url: Optional[str] = ""


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None


class SourceOut(BaseModel):
    id: str
    name: str
    source_type: str
    url: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Chat ─────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str   # user | assistant
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str
    notebook_id: str


# ── Notes ────────────────────────────────────────────────────────────
class NoteCreate(BaseModel):
    title: str = "New note"
    content: str = ""


class NoteOut(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
