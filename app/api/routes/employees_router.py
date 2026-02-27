"""API эндпоинты для работы с сотрудниками"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db
from app.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services import EmployeeService
from app.exceptions import EmployeeNotFoundError, DepartmentNotFoundError

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Получить сотрудника",
    description="Получает информацию о сотруднике по ID"
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Получить сотрудника по ID"""
    try:
        service = EmployeeService(db)
        return service.get_employee(employee_id)
    except EmployeeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=List[EmployeeResponse],
    summary="Получить список сотрудников",
    description="Получает список всех сотрудников с возможностью фильтрации"
)
def get_employees(
    department_id: Optional[int] = Query(None, description="Фильтр по подразделению"),
    search: Optional[str] = Query(None, description="Поиск по имени или должности"),
    skip: int = Query(0, ge=0, description="Количество пропущенных записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: Session = Depends(get_db)
):
    """Получить список сотрудников"""
    service = EmployeeService(db)
    
    try:
        if department_id:
            return service.get_employees_by_department(department_id)
        elif search:
            return service.search_employees(search)
        else:
            return service.get_all_employees(skip, limit)
    except DepartmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Обновить сотрудника",
    description="Обновляет информацию о сотруднике"
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    """Обновить сотрудника"""
    try:
        service = EmployeeService(db)
        return service.update_employee(employee_id, employee_data)
    except EmployeeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить сотрудника",
    description="Удаляет сотрудника из системы"
)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Удалить сотрудника"""
    try:
        service = EmployeeService(db)
        service.delete_employee(employee_id)
    except EmployeeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    return None