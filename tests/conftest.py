import sys
import os
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

# Принудительно устанавливаем переменные окружения
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Импортируем после установки переменных
from app.main import app
from app.database import Base
from app.api.deps import get_db
from app.models import Department, Employee

# Создаем единый движок для тестов
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Создание и очистка таблиц для каждого теста"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Создание тестовой БД для каждого теста с поддержкой транзакций"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем соединение и начинаем транзакцию
    connection = engine.connect()
    transaction = connection.begin()
    
    # Создаем сессию, привязанную к этому соединению
    session = TestingSessionLocal(bind=connection)
    
    # Очищаем таблицы перед тестом
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    
    # Начинаем вложенную транзакцию (savepoint)
    # Все операции в тесте будут в этой транзакции
    session.begin_nested()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Клиент для тестов"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()