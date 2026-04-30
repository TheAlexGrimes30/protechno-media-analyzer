import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.enums import ModuleType, Platform, PostStatus, PostType
from backend.db.posts import Post
from backend.db.users import User


async def list_posts(db: AsyncSession, user: User) -> list[Post]:
    result = await db.execute(
        select(Post)
        .where(Post.organization_id == user.organization_id)
        .order_by(Post.created_at.desc())
    )
    return list(result.scalars().all())


async def create_post(
    db: AsyncSession,
    user: User,
    title: str,
    text_draft: str,
    text_generated: str,
    tone: str,
    vk_post_id: str | None,
) -> Post:
    text_final = f"[тон: {tone}]\n{text_generated}" if tone else text_generated
    post = Post(
        title=title,
        text_draft=text_draft,
        text_generated=text_generated,
        text_final=text_final,
        post_type=PostType.other,
        status=PostStatus.published if vk_post_id else PostStatus.draft,
        module_type=ModuleType.events,
        platform=Platform.vk,
        external_id=vk_post_id,
        author_id=user.id,
        organization_id=user.organization_id,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def update_post_vk(
    db: AsyncSession,
    post_id: str,
    user: User,
    vk_post_id: str | None,
) -> Post | None:
    result = await db.execute(
        select(Post).where(Post.id == uuid.UUID(post_id), Post.organization_id == user.organization_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return None
    post.external_id = vk_post_id
    post.status = PostStatus.published if vk_post_id else PostStatus.draft
    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post_id: str, user: User) -> bool:
    result = await db.execute(
        select(Post).where(Post.id == uuid.UUID(post_id), Post.organization_id == user.organization_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        return False
    await db.delete(post)
    await db.commit()
    return True
