"""Pydantic схемы для Employee"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmployeeBase(BaseModel):
    """Базовая схема сотрудника"""
    full_name: str = Field(..., min_length=1, max_length=200, description="ФИО сотрудника")
    position: str = Field(..., min_length=1, max_length=200, description="Должность")
    hired_at: Optional[date] = Field(None, description="Дата приёма на работу")
    
    @field_validator('full_name', 'position')
    @classmethod
    def trim_fields(cls, v: str) -> str:
        """Обрезка пробелов по краям"""
        return v.strip()


class EmployeeCreate(EmployeeBase):
    """Схема для создания сотрудника"""
    pass

class EmployeeUpdate(BaseModel):
    """Схема для обновления сотрудника"""
    full_name: Optional[str] = None
    position: Optional[str] = None
    hired_at: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)

class EmployeeResponse(EmployeeBase):
    """Схема ответа с сотрудником"""
    id: int
    department_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

class EmployeeWithDepartment(EmployeeResponse):
    """Схема сотрудника с информацией о подразделении"""
    department_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
