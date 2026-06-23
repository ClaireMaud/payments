from fastapi import FastAPI

from app.api.v1.routes import payments

app = FastAPI(title="Payments Service")

app.include_router(payments.router, prefix="/api/v1")
