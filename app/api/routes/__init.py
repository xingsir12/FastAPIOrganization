"""API routes"""
from app.api.routes.departments_router import router as departments_router
from app.api.routes.employees_router import router as employees_router

__all__ = ["departments_router", "employees_router"]