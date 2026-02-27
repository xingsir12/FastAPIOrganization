"""Pydantic схемы для Department"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DepartmentBase(BaseModel):
    """Базовая схема подразделения"""
    name: str = Field(..., min_length=1, max_length=200, description="Название подразделения")
    
    @field_validator('name')
    @classmethod
    def trim_name(cls, v: str) -> str:
        """Обрезка пробелов по краям"""
        return v.strip()


class DepartmentCreate(DepartmentBase):
    """Схема для создания подразделения"""
    parent_id: Optional[int] = Field(None, description="ID родительского подразделения")


class DepartmentUpdate(BaseModel):
    """Схема для обновления подразделения"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Название подразделения")
    parent_id: Optional[int] = Field(None, description="ID родительского подразделения")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('name')
    @classmethod
    def trim_name(cls, v: Optional[str]) -> Optional[str]:
        """Обрезка пробелов по краям"""
        return v.strip() if v else v


class EmployeeInDepartment(BaseModel):
    """Краткая информация о сотруднике в подразделении"""
    id: int
    full_name: str
    position: str
    hired_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class DepartmentResponse(DepartmentBase):
    """Схема ответа с подразделением"""
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class DepartmentTree(DepartmentResponse):
    """Схема дерева подразделений с сотрудниками"""
    employees: List[EmployeeInDepartment] = Field(default_factory=list, description="Дочерние подразделения")
    children: List["DepartmentTree"] = Field(default_factory=list, description="Сотрудники подразделения")
    
    model_config = {"from_attributes": True}


# Необходимо для рекурсивных моделей
DepartmentTree.model_rebuild()