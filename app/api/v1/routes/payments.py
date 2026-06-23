from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.dependecies import verify_api_key
from app.models.payment import Payment
from app.repositories.payment import PaymentRepository
from app.schemas.payment import (
    PaymentCreate,
    PaymentCreatedResponse,
    PaymentResponse,
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=PaymentCreatedResponse,
)
async def create_payment(
    body: PaymentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(verify_api_key),
) -> PaymentCreatedResponse:
    repo = PaymentRepository(session)

    existing = await repo.get_by_idempotency_key(idempotency_key)
    if existing:
        return PaymentCreatedResponse(
            payment_id=existing.id,
            status=existing.status,
            created_at=existing.created_at,
        )

    payment = Payment(
        amount=body.amount,
        currency=body.currency,
        description=body.description,
        extra_data=body.metadata,
        idempotency_key=idempotency_key,
        webhook_url=str(body.webhook_url),
    )
    payment = await repo.create(payment)

    return PaymentCreatedResponse(
        payment_id=payment.id,
        status=payment.status,
        created_at=payment.created_at,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _: None = Depends(verify_api_key),
) -> PaymentResponse:
    repo = PaymentRepository(session)

    payment = await repo.get_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return PaymentResponse.model_validate(payment)
