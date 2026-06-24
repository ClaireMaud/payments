import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routes import payments
from app.broker import broker
from app.outbox.relay import run_relay


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    relay_task = asyncio.create_task(run_relay())
    yield
    relay_task.cancel()
    await broker.close()


app = FastAPI(title="Payments Service", lifespan=lifespan)

app.include_router(payments.router, prefix="/api/v1")
