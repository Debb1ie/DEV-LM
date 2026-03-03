from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import User, Notebook, Source
from auth import get_current_user
from schemas import NotebookCreate, NotebookUpdate, NotebookOut

router = APIRouter()


async def _get_notebook_or_404(
    notebook_id: str,
    user: User,
    db: AsyncSession,
) -> Notebook:
    result = await db.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.owner_id == user.id,
        )
    )
    nb = result.scalar_one_or_none()
    if not nb:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return nb


@router.get("", response_model=list[NotebookOut])
async def list_notebooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notebook).where(Notebook.owner_id == current_user.id)
        .order_by(Notebook.updated_at.desc())
    )
    notebooks = result.scalars().all()

    # Attach source counts
    out = []
    for nb in notebooks:
        src_count_res = await db.execute(
            select(func.count(Source.id)).where(Source.notebook_id == nb.id)
        )
        nb_out = NotebookOut.model_validate(nb)
        nb_out.source_count = src_count_res.scalar_one()
        out.append(nb_out)
    return out


@router.post("", response_model=NotebookOut, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    body: NotebookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb = Notebook(
        owner_id=current_user.id,
        name=body.name,
        description=body.description or "",
        category=body.category or "Backend",
    )
    db.add(nb)
    await db.flush()
    nb_out = NotebookOut.model_validate(nb)
    nb_out.source_count = 0
    return nb_out


@router.get("/{notebook_id}", response_model=NotebookOut)
async def get_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb = await _get_notebook_or_404(notebook_id, current_user, db)
    src_count = await db.execute(
        select(func.count(Source.id)).where(Source.notebook_id == nb.id)
    )
    nb_out = NotebookOut.model_validate(nb)
    nb_out.source_count = src_count.scalar_one()
    return nb_out


@router.patch("/{notebook_id}", response_model=NotebookOut)
async def update_notebook(
    notebook_id: str,
    body: NotebookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb = await _get_notebook_or_404(notebook_id, current_user, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(nb, field, value)
    await db.flush()
    nb_out = NotebookOut.model_validate(nb)
    return nb_out


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nb = await _get_notebook_or_404(notebook_id, current_user, db)
    await db.delete(nb)
