from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from database import get_db
from models import User, Notebook, Source, Message
from auth import get_current_user
from schemas import ChatRequest, ChatResponse
from config import settings

router = APIRouter()


async def _build_system_prompt(notebook: Notebook, sources: list[Source]) -> str:
    source_lines = []
    for s in sources:
        if s.content:
            # Truncate very large sources to avoid blowing the context window
            snippet = s.content[:4000] + ("..." if len(s.content) > 4000 else "")
            source_lines.append(f"### {s.name} ({s.source_type})\n{snippet}")
        elif s.url:
            source_lines.append(f"### {s.name} ({s.source_type})\nURL: {s.url}")
        else:
            source_lines.append(f"### {s.name} ({s.source_type})")

    sources_block = "\n\n".join(source_lines) if source_lines else "No sources added yet."

    return f"""You are DevLog AI, a precise developer knowledge assistant.

Notebook: "{notebook.name}"
Category: {notebook.category}
Description: {notebook.description or 'No description'}

--- SOURCES ---
{sources_block}
--- END SOURCES ---

Instructions:
- Answer questions grounded in the sources above whenever possible.
- Be concise and technical. Developers prefer precision over verbosity.
- Use code examples when helpful. Format code with triple backticks and language name.
- When citing information, reference the source name inline (e.g. "According to server.ts...").
- If a question cannot be answered from the sources, say so and offer general knowledge instead.
"""


@router.post("/{notebook_id}", response_model=ChatResponse)
async def chat(
    notebook_id: str,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    nb_result = await db.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.owner_id == current_user.id,
        )
    )
    notebook = nb_result.scalar_one_or_none()
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")

    # Load active sources
    src_result = await db.execute(
        select(Source).where(
            Source.notebook_id == notebook_id,
            Source.is_active == True,
        )
    )
    active_sources = src_result.scalars().all()

    system_prompt = await _build_system_prompt(notebook, active_sources)

    # Build messages array — use provided history + new user message
    messages = [{"role": m.role, "content": m.content} for m in body.history]
    messages.append({"role": "user", "content": body.message})

    # Call Anthropic API
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.ANTHROPIC_MODEL,
                    "max_tokens": settings.ANTHROPIC_MAX_TOKENS,
                    "system": system_prompt,
                    "messages": messages,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Anthropic API error: {e.response.status_code}",
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Could not reach Anthropic API")

    data = response.json()
    reply = data["content"][0]["text"]

    # Persist user message and AI reply
    db.add(Message(notebook_id=notebook_id, role="user",      content=body.message))
    db.add(Message(notebook_id=notebook_id, role="assistant", content=reply))
    await db.flush()

    return ChatResponse(reply=reply, notebook_id=notebook_id)


@router.get("/{notebook_id}/history")
async def get_history(
    notebook_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the last N messages for a notebook."""
    nb_result = await db.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.owner_id == current_user.id,
        )
    )
    if not nb_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Notebook not found")

    result = await db.execute(
        select(Message)
        .where(Message.notebook_id == notebook_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]


@router.delete("/{notebook_id}/history", status_code=204)
async def clear_history(
    notebook_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear all chat history for a notebook."""
    nb_result = await db.execute(
        select(Notebook).where(
            Notebook.id == notebook_id,
            Notebook.owner_id == current_user.id,
        )
    )
    if not nb_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Notebook not found")

    result = await db.execute(
        select(Message).where(Message.notebook_id == notebook_id)
    )
    for msg in result.scalars().all():
        await db.delete(msg)
