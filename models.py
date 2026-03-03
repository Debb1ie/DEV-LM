from sqlalchemy import (
    Column, String, Text, Boolean, Integer,
    ForeignKey, DateTime, func
)
from sqlalchemy.orm import relationship
from database import Base
import uuid


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id           = Column(String, primary_key=True, default=gen_uuid)
    email        = Column(String, unique=True, nullable=False, index=True)
    username     = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())

    notebooks    = relationship("Notebook", back_populates="owner", cascade="all, delete-orphan")


class Notebook(Base):
    __tablename__ = "notebooks"

    id           = Column(String, primary_key=True, default=gen_uuid)
    owner_id     = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name         = Column(String, nullable=False)
    description  = Column(Text, default="")
    category     = Column(String, default="Backend")   # Backend | Frontend | DevOps | Research | Architecture | Mobile
    is_shared    = Column(Boolean, default=False)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner        = relationship("User", back_populates="notebooks")
    sources      = relationship("Source",  back_populates="notebook", cascade="all, delete-orphan")
    messages     = relationship("Message", back_populates="notebook", cascade="all, delete-orphan")
    notes        = relationship("Note",    back_populates="notebook", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id           = Column(String, primary_key=True, default=gen_uuid)
    notebook_id  = Column(String, ForeignKey("notebooks.id"), nullable=False, index=True)
    name         = Column(String, nullable=False)
    source_type  = Column(String, default="file")   # file | url | github | npm | api_docs | paste
    content      = Column(Text, default="")
    url          = Column(String, default="")
    is_active    = Column(Boolean, default=True)    # whether it's selected in queries
    created_at   = Column(DateTime, server_default=func.now())

    notebook     = relationship("Notebook", back_populates="sources")


class Message(Base):
    __tablename__ = "messages"

    id           = Column(String, primary_key=True, default=gen_uuid)
    notebook_id  = Column(String, ForeignKey("notebooks.id"), nullable=False, index=True)
    role         = Column(String, nullable=False)   # user | assistant
    content      = Column(Text, nullable=False)
    created_at   = Column(DateTime, server_default=func.now())

    notebook     = relationship("Notebook", back_populates="messages")


class Note(Base):
    __tablename__ = "notes"

    id           = Column(String, primary_key=True, default=gen_uuid)
    notebook_id  = Column(String, ForeignKey("notebooks.id"), nullable=False, index=True)
    title        = Column(String, default="New note")
    content      = Column(Text, default="")
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())

    notebook     = relationship("Notebook", back_populates="notes")
