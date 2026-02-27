"""Сервис для работы с подразделениями"""
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Department
from app.schemas import DepartmentCreate, DepartmentUpdate
from app.repositories import DepartmentRepository, EmployeeRepository
from app.exceptions import (
    DepartmentNotFoundError,
    DepartmentNameConflictError,
    CircularReferenceError,
    SelfReferenceError,
    InvalidReassignDepartmentError,
)

logger = logging.getLogger(__name__)


class DepartmentService:
    """Сервис для работы с подразделениями"""
    
    def __init__(self, db: Session):
        """
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.repo = DepartmentRepository(db)
        self.employee_repo = EmployeeRepository(db)
    
    def get_department(self, department_id: int) -> Department:
        """Получить подразделение по ID"""
        department = self.repo.get_by_id(department_id)
        if not department:
            raise DepartmentNotFoundError(department_id)
        return department
    
    def get_department_with_tree(
        self,
        department_id: int,
        depth: int = 1,
        include_employees: bool = True,
        current_depth: int = 0
    ) -> Department:
        """Получить подразделение с деревом подразделений и сотрудниками"""
        if current_depth == 0:
            # Первый вызов - загружаем корневое подразделение
            department = self.get_department(department_id)
        else:
            department = self.repo.get_by_id(department_id)
            if not department:
                return None
        
        # Загружаем сотрудников если нужно
        if include_employees:
            department.employees = self.employee_repo.get_by_department(
                department_id, 
                order_by="full_name"
            )
        else:
            department.employees = []
        
        # Рекурсивно загружаем дочерние подразделения
        if current_depth < depth:
            children = self.repo.get_children(department_id)
            department.children = []
            for child in children:
                child_with_tree = self.get_department_with_tree(
                    child.id, depth, include_employees, current_depth + 1
                )
                if child_with_tree:
                    department.children.append(child_with_tree)
        else:
            department.children = []
        
        return department
    
    def create_department(self, department_data: DepartmentCreate) -> Department:
        """Создать новое подразделение"""
        # Проверка существования родителя
        if department_data.parent_id:
            if not self.repo.exists(department_data.parent_id):
                raise DepartmentNotFoundError(department_data.parent_id)
        
        # Проверка уникальности имени в родителе
        if self.repo.check_name_exists_in_parent(
            department_data.name, 
            department_data.parent_id
        ):
            raise DepartmentNameConflictError(department_data.name)
        
        # Создание подразделения
        department = Department(
            name=department_data.name,
            parent_id=department_data.parent_id
        )
        
        try:
            department = self.repo.create_from_obj(department)
            logger.info(f"Created department: {department.name} (ID: {department.id})")
            return department
        except IntegrityError as e:
            self.db.rollback()
            if "uq_department_name_parent" in str(e.orig):
                raise DepartmentNameConflictError(department_data.name)
            logger.error(f"Error creating department: {e}")
            raise
    
    def _check_circular_reference(
        self,
        department_id: int,
        new_parent_id: Optional[int]
    ) -> bool:
        """Проверка на циклическую ссылку"""
        if not new_parent_id:
            return False
        
        # Используем метод репозитория
        return self.repo.is_descendant_of(new_parent_id, department_id)
    
    def update_department(
        self,
        department_id: int,
        department_data: DepartmentUpdate
    ) -> Department:
        """Обновить подразделение"""
        department = self.get_department(department_id)
        
        # Проверка на self-reference
        if department_data.parent_id == department_id:
            raise SelfReferenceError()
        
        # Проверка на циклическую ссылку
        if department_data.parent_id is not None:
            if self._check_circular_reference(department_id, department_data.parent_id):
                raise CircularReferenceError()
            
            # Проверка существования нового родителя
            if department_data.parent_id and not self.repo.exists(department_data.parent_id):
                raise DepartmentNotFoundError(department_data.parent_id)
        
        # Проверка уникальности имени при изменении
        if department_data.name is not None:
            new_parent_id = (
                department_data.parent_id 
                if department_data.parent_id is not None 
                else department.parent_id
            )
            if self.repo.check_name_exists_in_parent(
                department_data.name,
                new_parent_id,
                exclude_id=department_id
            ):
                raise DepartmentNameConflictError(department_data.name)
        
        # Подготовка данных для обновления
        update_data = {}
        if department_data.name is not None:
            update_data['name'] = department_data.name
        if department_data.parent_id is not None:
            update_data['parent_id'] = department_data.parent_id
        
        try:
            department = self.repo.update(department, **update_data)
            logger.info(f"Updated department ID: {department_id}")
            return department
        except IntegrityError as e:
            self.db.rollback()
            if "uq_department_name_parent" in str(e.orig):
                raise DepartmentNameConflictError(department_data.name)
            logger.error(f"Error updating department: {e}")
            raise
    
    def delete_department_cascade(self, department_id: int) -> None:
        """Удалить подразделение каскадно (со всеми дочерними и сотрудниками)"""
        department = self.get_department(department_id)
        self.repo.delete(department)
        logger.info(f"Deleted department ID: {department_id} (cascade)")
    
    def delete_department_reassign(
        self,
        department_id: int,
        reassign_to_department_id: int
    ) -> None:
        """Удалить подразделение с переводом сотрудников в другое"""
        department = self.get_department(department_id)
        
        # Проверка существования департамента для переназначения
        if not self.repo.exists(reassign_to_department_id):
            raise InvalidReassignDepartmentError(
                f"Reassign department with id {reassign_to_department_id} not found"
            )
        
        # Проверка что не переносим в удаляемый департамент
        if reassign_to_department_id == department_id:
            raise InvalidReassignDepartmentError(
                "Cannot reassign employees to the department being deleted"
            )
        
        # Проверка что не переносим в дочерний департамент
        if self._check_circular_reference(department_id, reassign_to_department_id):
            raise InvalidReassignDepartmentError(
                "Cannot reassign to a child department"
            )
        
        # Перевод всех сотрудников
        self.employee_repo.reassign_to_department(department_id, reassign_to_department_id)
        
        # Перевод всех дочерних подразделений к родителю удаляемого
        self.repo.update_children_parent(department_id, department.parent_id)
        
        # Удаление подразделения
        self.repo.delete(department)
        logger.info(
            f"Deleted department ID: {department_id} "
            f"(reassigned to {reassign_to_department_id})"
        )