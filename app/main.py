from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routes import payments
from app.broker import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    yield
    await broker.close()


app = FastAPI(title="Payments Service", lifespan=lifespan)

app.include_router(payments.router, prefix="/api/v1")
