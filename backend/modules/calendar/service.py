import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.enums import EventSource
from backend.db.events import Event
from backend.db.users import User


def _pack_meta(description: str, start_time: str, end_time: str, status: str, platforms: list[str]) -> str:
    return json.dumps({
        "desc": description,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "platforms": platforms,
    }, ensure_ascii=False)


def _unpack_meta(raw: str | None) -> dict:
    default = {"desc": "", "start_time": "10:00", "end_time": "11:00", "status": "scheduled", "platforms": ["VK"]}
    if not raw:
        return default
    try:
        return {**default, **json.loads(raw)}
    except Exception:
        return default


async def list_events(db: AsyncSession, user: User) -> list[Event]:
    result = await db.execute(
        select(Event)
        .where(Event.organization_id == user.organization_id)
        .order_by(Event.event_date.asc())
    )
    return list(result.scalars().all())


async def create_event(
    db: AsyncSession,
    user: User,
    title: str,
    date: str,
    description: str,
    start_time: str,
    end_time: str,
    ev_status: str,
    platforms: list[str],
) -> Event:
    event_date = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
    event = Event(
        title=title,
        description=_pack_meta(description, start_time, end_time, ev_status, platforms),
        event_date=event_date,
        source=EventSource.manual,
        organization_id=user.organization_id,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def update_event(
    db: AsyncSession,
    event_id: str,
    user: User,
    title: str,
    date: str,
    description: str,
    start_time: str,
    end_time: str,
    ev_status: str,
    platforms: list[str],
) -> Event | None:
    result = await db.execute(
        select(Event).where(Event.id == uuid.UUID(event_id), Event.organization_id == user.organization_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        return None
    event.title = title
    event.event_date = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
    event.description = _pack_meta(description, start_time, end_time, ev_status, platforms)
    await db.commit()
    await db.refresh(event)
    return event


async def delete_event(db: AsyncSession, event_id: str, user: User) -> bool:
    result = await db.execute(
        select(Event).where(Event.id == uuid.UUID(event_id), Event.organization_id == user.organization_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        return False
    await db.delete(event)
    await db.commit()
    return True
