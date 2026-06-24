from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import Outbox


def enqueue_event(
    session: AsyncSession, event_type: str, payload: dict
) -> None:
    session.add(Outbox(event_type=event_type, payload=payload))
