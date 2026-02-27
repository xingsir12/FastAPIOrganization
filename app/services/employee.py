"""Сервис для работы с сотрудниками"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.repositories import DepartmentRepository, EmployeeRepository
from app.exceptions import DepartmentNotFoundError, EmployeeNotFoundError

logger = logging.getLogger(__name__)


class EmployeeService:
    """Сервис для работы с сотрудниками"""
    
    def __init__(self, db: Session):
        """
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.repo = EmployeeRepository(db)
        self.department_repo = DepartmentRepository(db)
    
    def get_employee(self, employee_id: int) -> Employee:
        """Получить сотрудника по ID"""
        employee = self.repo.get_by_id(employee_id)
        if not employee:
            raise EmployeeNotFoundError(employee_id)
        return employee
    
    def get_all_employees(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Получить всех сотрудников"""
        return self.repo.get_all(skip, limit)
    
    def get_employees_by_department(
        self,
        department_id: int,
        order_by: str = "full_name"
    ) -> List[Employee]:
        """Получить сотрудников подразделения"""
        # Проверка существования подразделения
        if not self.department_repo.exists(department_id):
            raise DepartmentNotFoundError(department_id)
        
        return self.repo.get_by_department(department_id, order_by)
    
    def search_employees(self, search_term: str) -> List[Employee]:
        """Поиск сотрудников по имени или должности"""
        if not search_term or len(search_term) < 2:
            return []
        
        # Ищем по имени
        by_name = self.repo.search_by_name(search_term)
        
        # Ищем по должности
        by_position = self.repo.search_by_position(search_term)
        
        # Объединяем и убираем дубликаты
        all_employees = {emp.id: emp for emp in by_name + by_position}
        return list(all_employees.values())
    
    def create_employee(
        self,
        department_id: int,
        employee_data: EmployeeCreate
    ) -> Employee:
        """Создать нового сотрудника в подразделении"""
        # Проверка существования подразделения
        if not self.department_repo.exists(department_id):
            raise DepartmentNotFoundError(department_id)
        
        # Создание сотрудника
        employee = Employee(
            department_id=department_id,
            full_name=employee_data.full_name,
            position=employee_data.position,
            hired_at=employee_data.hired_at
        )
        
        employee = self.repo.create_from_obj(employee)
        logger.info(
            f"Created employee: {employee.full_name} "
            f"in department {department_id} (ID: {employee.id})"
        )
        return employee
    
    def update_employee(
        self,
        employee_id: int,
        employee_data: EmployeeUpdate
    ) -> Employee:
        """Обновить данные сотрудника"""
        employee = self.get_employee(employee_id)
        
        # Подготовка данных для обновления (только переданные поля)
        update_data = {}
        if employee_data.full_name is not None:
            update_data['full_name'] = employee_data.full_name
        if employee_data.position is not None:
            update_data['position'] = employee_data.position
        if employee_data.hired_at is not None:
            update_data['hired_at'] = employee_data.hired_at
        
        if not update_data:
            # Ничего не обновляем
            return employee
        
        employee = self.repo.update(employee, **update_data)
        logger.info(f"Updated employee ID: {employee_id}")
        return employee
    
    def delete_employee(self, employee_id: int) -> None:
        """Удалить сотрудника"""
        employee = self.get_employee(employee_id)
        self.repo.delete(employee)
        logger.info(f"Deleted employee ID: {employee_id}")