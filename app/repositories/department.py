"""Репозиторий для работы с подразделениями"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models import Department
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """Репозиторий для работы с подразделениями"""
    
    def __init__(self, db: Session):
        super().__init__(Department, db)
    
    def get_by_id_with_relations(self, department_id: int) -> Optional[Department]:
        """Получить подразделение с загруженными отношениями"""
        return (
            self.db.query(Department)
            .options(joinedload(Department.employees))
            .filter(Department.id == department_id)
            .first()
        )
    
    def get_children(self, parent_id: int) -> List[Department]:
        """Получить все дочерние подразделения"""
        return (
            self.db.query(Department)
            .filter(Department.parent_id == parent_id)
            .all()
        )
    
    def get_root_departments(self) -> List[Department]:
        """Получить все корневые подразделения (без родителя)"""
        return (
            self.db.query(Department)
            .filter(Department.parent_id.is_(None))
            .all()
        )
    
    def check_name_exists_in_parent(
        self, 
        name: str, 
        parent_id: Optional[int],
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Проверить существует ли подразделение с таким именем у данного родителя
        
        Args:
            name: Название подразделения
            parent_id: ID родительского подразделения
            exclude_id: ID подразделения для исключения (при обновлении)
        """
        query = self.db.query(Department).filter(
            and_(
                Department.name == name,
                Department.parent_id == parent_id
            )
        )
        
        if exclude_id:
            query = query.filter(Department.id != exclude_id)
        
        return query.first() is not None
    
    def get_all_descendants(self, department_id: int) -> List[int]:
        """
        Получить все ID потомков подразделения (рекурсивно)
        
        Args:
            department_id: ID подразделения
            
        Returns:
            Список ID всех потомков
        """
        descendants = []
        children = self.get_children(department_id)
        
        for child in children:
            descendants.append(child.id)
            # Рекурсивно получаем потомков каждого ребенка
            descendants.extend(self.get_all_descendants(child.id))
        
        return descendants
    
    def is_descendant_of(self, department_id: int, potential_ancestor_id: int) -> bool:
        """
        Проверить является ли подразделение потомком другого подразделения
        
        Args:
            department_id: ID проверяемого подразделения
            potential_ancestor_id: ID потенциального предка
        """
        descendants = self.get_all_descendants(potential_ancestor_id)
        return department_id in descendants
    
    def get_path_to_root(self, department_id: int) -> List[Department]:
        """
        Получить путь от подразделения до корня
        
        Args:
            department_id: ID подразделения
            
        Returns:
            Список подразделений от текущего до корня
        """
        path = []
        current_id = department_id
        visited = set()  # Защита от циклов
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            department = self.get_by_id(current_id)
            
            if not department:
                break
            
            path.append(department)
            current_id = department.parent_id
        
        return path
    
    def update_children_parent(self, old_parent_id: int, new_parent_id: Optional[int]) -> None:
        """
        Обновить родителя для всех дочерних подразделений
        
        Args:
            old_parent_id: Старый ID родителя
            new_parent_id: Новый ID родителя
        """
        self.db.query(Department).filter(
            Department.parent_id == old_parent_id
        ).update({"parent_id": new_parent_id})        
    
    def count_children(self, department_id: int) -> int:
        """Подсчитать количество дочерних подразделений"""
        return (
            self.db.query(Department)
            .filter(Department.parent_id == department_id)
            .count()
        )