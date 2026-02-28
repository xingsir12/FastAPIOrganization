"""Тесты для API подразделений"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Department, Employee

def test_create_department_with_parent(client: TestClient, db: Session):
    """Тест создания подразделения с родителем"""
    # Проверим, что таблицы существуют (для отладки)
    from sqlalchemy import inspect
    inspector = inspect(db.bind)
    print(f"Таблицы: {inspector.get_table_names()}")
    
    parent = Department(name="Parent")
    db.add(parent)
    db.commit()
    db.refresh(parent)
    
    response = client.post(
        "/api/v1/departments/",
        json={"name": "Child", "parent_id": parent.id}
    )
    assert response.status_code == 201

def test_get_department_tree(client: TestClient, db: Session):
    """Тест получения дерева подразделений"""
    root = Department(name="Root")
    db.add(root)
    db.commit()
    db.refresh(root)

    child = Department(name="Child", parent_id=root.id)
    db.add(child)
    db.commit()
    db.refresh(child)

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
    assert "cannot be its own parent" in response.json()["detail"].lower()


def test_delete_department_cascade(client: TestClient, db: Session):
    """Тест каскадного удаления"""
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

    root_id = root.id

    response = client.delete(f"/api/v1/departments/{root_id}?mode=cascade")
    assert response.status_code == 204

    response = client.get(f"/api/v1/departments/{root_id}")
    assert response.status_code == 404


def test_delete_department_reassign(client: TestClient, db: Session):
    """Тест удаления с переназначением"""
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

    to_delete_id = to_delete.id
    target_id = target.id
    employee_id = employee.id

    response = client.delete(
        f"/api/v1/departments/{to_delete_id}",
        params={"mode": "reassign", "reassign_to_department_id": target_id}
    )
    assert response.status_code == 204

    response = client.get(f"/api/v1/employees/{employee_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["department_id"] == target_id