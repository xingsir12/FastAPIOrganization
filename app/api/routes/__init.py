"""API routes"""
from app.api.routes.departments import router as departments_router
from app.api.routes.employees import router as employees_router

__all__ = ["departments_router", "employees_router"]