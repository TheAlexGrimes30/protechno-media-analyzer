from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.db.events import Event
from backend.db.users import User
from backend.modules.auth.deps import get_current_user
from backend.modules.calendar import service

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


class EventCreateRequest(BaseModel):
    title: str
    date: str
    description: str = ""
    start_time: str = "10:00"
    end_time: str = "11:00"
    status: str = "scheduled"
    platforms: list[str] = ["VK"]


class EventResponse(BaseModel):
    id: str
    title: str
    date: str
    start_time: str
    end_time: str
    description: str
    status: str
    platforms: list[str]

    @classmethod
    def from_orm(cls, event: Event) -> "EventResponse":
        meta = service._unpack_meta(event.description)
        return cls(
            id=str(event.id),
            title=event.title,
            date=event.event_date.strftime("%Y-%m-%d"),
            start_time=meta["start_time"],
            end_time=meta["end_time"],
            description=meta["desc"],
            status=meta["status"],
            platforms=meta["platforms"],
        )


@router.get("/", response_model=list[EventResponse])
async def list_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[EventResponse]:
    events = await service.list_events(db, current_user)
    return [EventResponse.from_orm(e) for e in events]


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    event = await service.create_event(
        db, current_user,
        title=payload.title,
        date=payload.date,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time,
        ev_status=payload.status,
        platforms=payload.platforms,
    )
    return EventResponse.from_orm(event)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    payload: EventCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    event = await service.update_event(
        db, event_id, current_user,
        title=payload.title,
        date=payload.date,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time,
        ev_status=payload.status,
        platforms=payload.platforms,
    )
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
    return EventResponse.from_orm(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await service.delete_event(db, event_id, current_user)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Событие не найдено")
