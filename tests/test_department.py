"""Тесты для API подразделений"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Department, Employee
from app.main import app


def test_create_department(client: TestClient):
    """Тест создания подразделения"""
    response = client.post("/api/v1/departments/", json={"name": "IT Department"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "IT Department"
    assert data["parent_id"] is None
    assert "id" in data


def test_create_department_with_parent(client: TestClient, db: Session):
    """Тест создания подразделения с родителем"""
    # Создаем родительское подразделение
    parent = Department(name="Parent")
    db.add(parent)
    db.commit()
    db.refresh(parent)
    
    response = client.post(
        "/api/v1/departments/", 
        json={"name": "Child", "parent_id": parent.id}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Child"
    assert data["parent_id"] == parent.id


def test_create_department_duplicate_name(client: TestClient, db: Session):
    """Тест создания подразделения с дубликатом имени"""
    # Создаем подразделение
    dept = Department(name="HR")
    db.add(dept)
    db.commit()
    
    # Пытаемся создать еще одно с таким же именем
    response = client.post("/api/v1/departments/", json={"name": "HR"})
    assert response.status_code == 409  # Conflict


def test_get_department_tree(client: TestClient, db: Session):
    """Тест получения дерева подразделений"""
    # Создаем структуру
    root = Department(name="Root")
    db.add(root)
    db.commit()
    db.refresh(root)
    
    child = Department(name="Child", parent_id=root.id)
    db.add(child)
    db.commit()
    db.refresh(child)
    
    # Добавляем сотрудника
    employee = Employee(
        full_name="John Doe",
        position="Developer",
        department_id=child.id
    )
    db.add(employee)
    db.commit()
    
    response = client.get(f"/api/v1/departments/{root.id}?depth=2&include_employees=true")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Root"
    assert len(data["children"]) == 1
    assert data["children"][0]["name"] == "Child"
    assert len(data["children"][0]["employees"]) == 1
    assert data["children"][0]["employees"][0]["full_name"] == "John Doe"


def test_update_department(client: TestClient, db: Session):
    """Тест обновления подразделения"""
    dept = Department(name="Old Name")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    
    response = client.patch(
        f"/api/v1/departments/{dept.id}",
        json={"name": "New Name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"


def test_update_department_self_parent(client: TestClient, db: Session):
    """Тест попытки сделать подразделение родителем самого себя"""
    dept = Department(name="Test")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    
    response = client.patch(
        f"/api/v1/departments/{dept.id}",
        json={"parent_id": dept.id}
    )
    assert response.status_code == 400
    assert "cannot be parent of itself" in response.json()["detail"].lower()


def test_delete_department_cascade(client: TestClient, db: Session):
    """Тест каскадного удаления"""
    # Создаем структуру
    root = Department(name="Root")
    db.add(root)
    db.commit()
    db.refresh(root)
    
    child = Department(name="Child", parent_id=root.id)
    db.add(child)
    db.commit()
    db.refresh(child)
    
    employee = Employee(
        full_name="Jane Doe",
        position="Manager",
        department_id=child.id
    )
    db.add(employee)
    db.commit()
    
    # Удаляем каскадно
    response = client.delete(f"/api/v1/departments/{root.id}?mode=cascade")
    assert response.status_code == 204
    
    # Проверяем что все удалилось
    assert db.query(Department).count() == 0
    assert db.query(Employee).count() == 0


def test_delete_department_reassign(client: TestClient, db: Session):
    """Тест удаления с переназначением"""
    # Создаем структуру
    root = Department(name="Root")
    db.add(root)
    db.commit()
    db.refresh(root)
    
    target = Department(name="Target", parent_id=root.id)
    db.add(target)
    db.commit()
    db.refresh(target)
    
    to_delete = Department(name="ToDelete", parent_id=root.id)
    db.add(to_delete)
    db.commit()
    db.refresh(to_delete)
    
    employee = Employee(
        full_name="Jane Doe",
        position="Manager",
        department_id=to_delete.id
    )
    db.add(employee)
    db.commit()
    
    # Удаляем с переназначением
    response = client.delete(
        f"/api/v1/departments/{to_delete.id}",
        params={"mode": "reassign", "reassign_to_department_id": target.id}
    )
    assert response.status_code == 204
    
    # Проверяем что сотрудник переназначен
    updated_employee = db.query(Employee).first()
    assert updated_employee.department_id == target.id