"""API эндпоинты для работы с подразделениями"""
from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentTree,
    EmployeeCreate,
    EmployeeResponse,
)
from app.services import DepartmentService, EmployeeService
from app.exceptions import (
    DepartmentNotFoundError,
    DepartmentNameConflictError,
    CircularReferenceError,
    SelfReferenceError,
    InvalidReassignDepartmentError,
)

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать подразделение",
    description="Создает новое подразделение с указанным названием и опциональным родителем"
)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db)
):
    """Создать новое подразделение"""
    try:
        service = DepartmentService(db)
        return service.create_department(department_data)
    except DepartmentNameConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except DepartmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{department_id}/employees/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать сотрудника в подразделении",
    description="Создает нового сотрудника в указанном подразделении"
)
def create_employee(
    department_id: int,
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Создать сотрудника в подразделении"""
    try:
        service = EmployeeService(db)
        return service.create_employee(department_id, employee_data)
    except DepartmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/{department_id}",
    response_model=DepartmentTree,
    summary="Получить подразделение с деревом",
    description="Получает подразделение со всеми сотрудниками и вложенными подразделениями до указанной глубины"
)
def get_department_tree(
    department_id: int,
    depth: int = Query(default=1, ge=1, le=5, description="Глубина вложенности подразделений"),
    include_employees: bool = Query(default=True, description="Включить сотрудников в ответ"),
    db: Session = Depends(get_db)
):
    """Получить подразделение с деревом и сотрудниками"""
    try:
        service = DepartmentService(db)
        return service.get_department_with_tree(
            department_id,
            depth=depth,
            include_employees=include_employees
        )
    except DepartmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Обновить подразделение",
    description="Обновляет название и/или родителя подразделения"
)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db)
):
    """Обновить подразделение"""
    try:
        service = DepartmentService(db)
        return service.update_department(department_id, department_data)
    except DepartmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DepartmentNameConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (SelfReferenceError, CircularReferenceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить подразделение",
    description=(
        "Удаляет подразделение.\n\n"
        "**cascade** - удаляет подразделение со всеми дочерними подразделениями и сотрудниками\n\n"
        "**reassign** - удаляет подразделение, переводя сотрудников в другое подразделение, "
        "а дочерние подразделения - к родителю удаляемого"
    )
)
def delete_department(
    department_id: int,
    mode: Literal["cascade", "reassign"] = Query(..., description="Режим удаления"),
    reassign_to_department_id: Optional[int] = Query(
        None,
        description="ID для перенаправления (обязателен при mode=reassign)"
    ),
    db: Session = Depends(get_db)
):
    """Удалить подразделение"""
    service = DepartmentService(db)
    
    try:
        if mode == "cascade":
            service.delete_department_cascade(department_id)
        elif mode == "reassign":
            if not reassign_to_department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="reassign_to_department_id is required when mode=reassign"
                )
            service.delete_department_reassign(department_id, reassign_to_department_id)
    except DepartmentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidReassignDepartmentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return None