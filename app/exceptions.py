"""Кастомные исключения"""


class AppException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DepartmentNotFoundError(AppException):
    """Подразделение не найдено"""
    def __init__(self, department_id: int):
        super().__init__(
            message=f"Department with id {department_id} not found",
            status_code=404
        )


class EmployeeNotFoundError(AppException):
    """Сотрудник не найден"""
    def __init__(self, employee_id: int):
        super().__init__(
            message=f"Employee with id {employee_id} not found",
            status_code=404
        )


class DepartmentNameConflictError(AppException):
    """Конфликт имени подразделения"""
    def __init__(self, name: str):
        super().__init__(
            message=f"Department with name '{name}' already exists in this parent",
            status_code=409
        )


class CircularReferenceError(AppException):
    """Циклическая ссылка в дереве подразделений"""
    def __init__(self):
        super().__init__(
            message="Cannot create circular reference in department tree",
            status_code=409
        )


class SelfReferenceError(AppException):
    """Подразделение не может быть родителем самого себя"""
    def __init__(self):
        super().__init__(
            message="Department cannot be its own parent",
            status_code=400
        )


class InvalidReassignDepartmentError(AppException):
    """Некорректное подразделение для переназначения"""
    def __init__(self, detail: str):
        super().__init__(
            message=detail,
            status_code=400
        )