from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, HttpUrl

from app.models.payment import Currency, PaymentStatus


class PaymentCreate(BaseModel):
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict | None = None
    webhook_url: HttpUrl


class PaymentCreatedResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict | None = Field(
        None,
        validation_alias=AliasChoices("extra_data", "metadata"),
    )
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None = None
