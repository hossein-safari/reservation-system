from fastapi import APIRouter

from app.api.controllers import auth, health, payments, reservations, resources, slots, transactions

router = APIRouter()
v1 = APIRouter(prefix="/api/v1")
v1.include_router(auth.router)
v1.include_router(resources.router)
v1.include_router(slots.router)
v1.include_router(reservations.router)
v1.include_router(payments.router)
v1.include_router(transactions.router)
router.include_router(v1)
router.include_router(health.router)
