import asyncio
import logging

from app.broker import broker
from app.db.session import async_session_factory
from app.queues import payments_exchange, payments_queue
from app.repositories.outbox import OutboxRepository

logger = logging.getLogger(__name__)

POLL_INTERVAL = 5
MAX_RETRIES = 3


async def run_relay() -> None:
    while True:
        try:
            await _process_pending()
        except Exception:
            logger.exception("Relay iteration failed")
        await asyncio.sleep(POLL_INTERVAL)


async def _process_pending() -> None:
    async with async_session_factory() as session:
        repo = OutboxRepository(session)
        pending = await repo.get_pending()

    for outbox in pending:
        async with async_session_factory() as session:
            repo = OutboxRepository(session)
            try:
                await broker.publish(
                    outbox.payload,
                    queue=payments_queue,
                    exchange=payments_exchange,
                )
                await repo.mark_sent(outbox.id)
            except Exception:
                logger.exception("Failed to publish outbox row %s", outbox.id)
                await repo.increment_retry(outbox.id, MAX_RETRIES)
            await session.commit()
