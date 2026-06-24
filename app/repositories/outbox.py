from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import Outbox, OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def create(self, outbox: Outbox) -> None:
        self.session.add(outbox)

    async def get_pending(self, limit: int = 100) -> list[Outbox]:
        result = await self.session.execute(
            select(Outbox)
            .where(Outbox.status == OutboxStatus.pending)
            .order_by(Outbox.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_sent(self, outbox_id: UUID) -> None:
        outbox = await self.session.get(Outbox, outbox_id)
        if outbox:
            outbox.status = OutboxStatus.sent
            outbox.sent_at = datetime.now(timezone.utc)

    async def mark_failed(self, outbox_id: UUID) -> None:
        outbox = await self.session.get(Outbox, outbox_id)
        if outbox:
            outbox.status = OutboxStatus.failed
