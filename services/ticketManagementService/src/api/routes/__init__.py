# This file makes the routes directory a Python package 

from fastapi import APIRouter
from .bookings import router as bookings_router
from .tickets import router as tickets_router

router = APIRouter()
router.include_router(bookings_router)
router.include_router(tickets_router)

__all__ = ["router"] 