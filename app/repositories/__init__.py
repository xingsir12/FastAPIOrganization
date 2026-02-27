"""Репозитории для работы с БД"""
from app.repositories.base import BaseRepository
from app.repositories.department import DepartmentRepository
from app.repositories.employee import EmployeeRepository

__all__ = [
    "BaseRepository",
    "DepartmentRepository",
    "EmployeeRepository",
]