from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, Notebook, Source
from auth import get_current_user
from schemas import SourceCreate, SourceUpdate, SourceOut

router = APIRouter()

VALID_TYPES = {"file", "url", "github", "npm", "api_docs", "paste"}


async def _own_notebook(notebook_id: str, user: User, db: AsyncSession) -> Notebook:
    result = await db.execute(
        select(Notebook).where(Notebook.id == notebook_id, Notebook.owner_id == user.id)
    )
    nb = result.scalar_one_or_none()
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return nb


@router.get("/{notebook_id}/sources", response_model=list[SourceOut])
async def list_sources(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _own_notebook(notebook_id, current_user, db)
    result = await db.execute(
        select(Source)
        .where(Source.notebook_id == notebook_id)
        .order_by(Source.created_at.asc())
    )
    return result.scalars().all()


@router.post("/{notebook_id}/sources", response_model=SourceOut, status_code=status.HTTP_201_CREATED)
async def add_source(
    notebook_id: str,
    body: SourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _own_notebook(notebook_id, current_user, db)

    if body.source_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"source_type must be one of {VALID_TYPES}")

    src = Source(
        notebook_id=notebook_id,
        name=body.name,
        source_type=body.source_type,
        content=body.content or "",
        url=body.url or "",
    )
    db.add(src)
    await db.flush()
    return src


@router.patch("/{notebook_id}/sources/{source_id}", response_model=SourceOut)
async def update_source(
    notebook_id: str,
    source_id: str,
    body: SourceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _own_notebook(notebook_id, current_user, db)
    result = await db.execute(
        select(Source).where(Source.id == source_id, Source.notebook_id == notebook_id)
    )
    src = result.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(src, field, value)
    await db.flush()
    return src


@router.delete("/{notebook_id}/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    notebook_id: str,
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _own_notebook(notebook_id, current_user, db)
    result = await db.execute(
        select(Source).where(Source.id == source_id, Source.notebook_id == notebook_id)
    )
    src = result.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")
    await db.delete(src)
