import asyncio
import logging
import random
from datetime import datetime, timezone
from uuid import UUID

import httpx
from faststream import FastStream
from tenacity import retry, stop_after_attempt, wait_exponential

from app.broker import broker
from app.db.session import async_session_factory
from app.models.payment import PaymentStatus
from app.queues import payments_exchange, payments_queue
from app.repositories.payment import PaymentRepository

logger = logging.getLogger(__name__)

faststream_app = FastStream(broker)

GATEWAY_SUCCESS_RATE = 0.9
GATEWAY_MIN_DELAY = 2
GATEWAY_MAX_DELAY = 5


@broker.subscriber(payments_queue, exchange=payments_exchange)
async def handle_payment(payload: dict) -> None:
    payment_id = UUID(payload["payment_id"])

    async with async_session_factory() as session:
        repo = PaymentRepository(session)
        payment = await repo.get_by_id(payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return

        delay = random.uniform(GATEWAY_MIN_DELAY, GATEWAY_MAX_DELAY)
        await asyncio.sleep(delay)

        if random.random() < GATEWAY_SUCCESS_RATE:
            payment.status = PaymentStatus.succeeded
        else:
            payment.status = PaymentStatus.failed

        payment.processed_at = datetime.now(timezone.utc)
        await session.commit()

    try:
        await _send_webhook(
            payment.webhook_url, str(payment_id), payment.status
        )
    except Exception:
        logger.error(
            f"Webhook failed for payment {payment_id} after all retries"
        )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    reraise=False,
)
async def _send_webhook(
    webhook_url: str, payment_id: str, status: PaymentStatus
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            webhook_url,
            json={"payment_id": payment_id, "status": status},
            timeout=10,
        )
        response.raise_for_status()


if __name__ == "__main__":
    asyncio.run(faststream_app.run())
