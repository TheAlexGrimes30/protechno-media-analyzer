from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.db.database import get_db
from backend.db.users import User
from backend.modules.auth.deps import get_current_user
from backend.modules.posts import service

router = APIRouter(prefix="/api/posts", tags=["posts"])


class PostCreateRequest(BaseModel):
    title: str
    text_draft: str = ""
    text_generated: str = ""
    tone: str = ""
    vk_post_id: str | None = None


class PostUpdateVkRequest(BaseModel):
    vk_post_id: str | None = None


class PostResponse(BaseModel):
    id: str
    title: str
    text_draft: str | None
    text_generated: str | None
    tone: str
    vk_post_id: str | None
    vk_wall_url: str | None
    status: str
    created_at: str

    @classmethod
    def from_orm(cls, post) -> "PostResponse":
        tone = ""
        gen = post.text_generated or ""
        if post.text_final and post.text_final.startswith("[тон:"):
            first_line = post.text_final.split("\n", 1)[0]
            tone = first_line.removeprefix("[тон: ").removesuffix("]")

        vk_url = None
        if post.external_id:
            vk_url = f"https://vk.com/wall-{settings.GROUP_ID}_{post.external_id}"

        return cls(
            id=str(post.id),
            title=post.title,
            text_draft=post.text_draft,
            text_generated=gen,
            tone=tone,
            vk_post_id=post.external_id,
            vk_wall_url=vk_url,
            status=post.status.value,
            created_at=post.created_at.isoformat(),
        )


@router.get("/", response_model=list[PostResponse])
async def list_posts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    posts = await service.list_posts(db, current_user)
    return [PostResponse.from_orm(p) for p in posts]


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    post = await service.create_post(
        db, current_user,
        title=payload.title,
        text_draft=payload.text_draft,
        text_generated=payload.text_generated,
        tone=payload.tone,
        vk_post_id=payload.vk_post_id,
    )
    return PostResponse.from_orm(post)


@router.patch("/{post_id}/vk", response_model=PostResponse)
async def update_post_vk(
    post_id: str,
    payload: PostUpdateVkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    post = await service.update_post_vk(db, post_id, current_user, payload.vk_post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")
    return PostResponse.from_orm(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await service.delete_post(db, post_id, current_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")
