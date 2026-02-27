"""Кастомные исключения"""
from fastapi import HTTPException, status

class AppException(Exception):
    """Базовое исключение приложения"""
    pass

class DepartmentNotFoundError(HTTPException):
    """Подразделение не найдено"""
    def __init__(self, department_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with id {department_id} not found"
        )


class EmployeeNotFoundError(HTTPException):
    """Сотрудник не найден"""
    def __init__(self, employee_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )


class DepartmentNameConflictError(HTTPException):
    """Конфликт имени подразделения"""
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Department with name '{name}' already exists in this parent"
        )


class CircularReferenceError(HTTPException):
    """Циклическая ссылка в дереве подразделений"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot create circular reference in department tree"
        )


class SelfReferenceError(HTTPException):
    """Подразделение не может быть родителем самого себя"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department cannot be its own parent"
        )


class InvalidReassignDepartmentError(HTTPException):
    """Некорректное подразделение для переназначения"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )