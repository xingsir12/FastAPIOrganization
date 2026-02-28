"""Репозиторий для работы с сотрудниками"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """Репозиторий для работы с сотрудниками"""
    
    def __init__(self, db: Session):
        super().__init__(Employee, db)
    
    def get_by_department(
        self, 
        department_id: int,
        order_by: str = "full_name"
    ) -> List[Employee]:
        """
        Получить всех сотрудников подразделения
        
        Args:
            department_id: ID подразделения
            order_by: Поле для сортировки (full_name, created_at, position)
        """
        query = self.db.query(Employee).filter(
            Employee.department_id == department_id
        )
        
        # Сортировка
        if order_by == "created_at":
            query = query.order_by(Employee.created_at)
        elif order_by == "position":
            query = query.order_by(Employee.position)
        else:
            query = query.order_by(Employee.full_name)
        
        return query.all()
    
    def get_by_departments(
        self, 
        department_ids: List[int],
        order_by: str = "full_name"
    ) -> List[Employee]:
        """
        Получить всех сотрудников из нескольких подразделений
        
        Args:
            department_ids: Список ID подразделений
            order_by: Поле для сортировки
        """
        query = self.db.query(Employee).filter(
            Employee.department_id.in_(department_ids)
        )
        
        if order_by == "created_at":
            query = query.order_by(Employee.created_at)
        elif order_by == "position":
            query = query.order_by(Employee.position)
        else:
            query = query.order_by(Employee.full_name)
        
        return query.all()
    
    def search_by_name(self, search_term: str) -> List[Employee]:
        """
        Поиск сотрудников по имени
        
        Args:
            search_term: Строка для поиска
        """
        return (
            self.db.query(Employee)
            .filter(Employee.full_name.ilike(f"%{search_term}%"))
            .order_by(Employee.full_name)
            .all()
        )
    
    def search_by_position(self, position: str) -> List[Employee]:
        """
        Поиск сотрудников по должности
        
        Args:
            position: Должность
        """
        return (
            self.db.query(Employee)
            .filter(Employee.position.ilike(f"%{position}%"))
            .order_by(Employee.full_name)
            .all()
        )
    
    def get_hired_between(
        self, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Employee]:
        """
        Получить сотрудников, нанятых в указанный период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
        """
        query = self.db.query(Employee)
        
        if start_date:
            query = query.filter(Employee.hired_at >= start_date)
        
        if end_date:
            query = query.filter(Employee.hired_at <= end_date)
        
        return query.order_by(Employee.hired_at.desc()).all()
    
    def count_by_department(self, department_id: int) -> int:
        """Подсчитать количество сотрудников в подразделении"""
        return (
            self.db.query(Employee)
            .filter(Employee.department_id == department_id)
            .count()
        )
    
    def reassign_to_department(
        self, 
        from_department_id: int,
        to_department_id: int
    ) -> int:
        """
        Переместить всех сотрудников из одного подразделения в другое
        
        Args:
            from_department_id: ID исходного подразделения
            to_department_id: ID целевого подразделения
            
        Returns:
            Количество перемещенных сотрудников
        """
        result = self.db.query(Employee).filter(
            Employee.department_id == from_department_id
        ).update({"department_id": to_department_id})
        
        return result
    
    def delete_by_department(self, department_id: int) -> int:
        """
        Удалить всех сотрудников подразделения
        
        Args:
            department_id: ID подразделения
            
        Returns:
            Количество удаленных сотрудников
        """
        result = self.db.query(Employee).filter(
            Employee.department_id == department_id
        ).delete()
        
        self.db.commit()
        return result