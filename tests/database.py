"""Тестовая конфигурация БД - полностью независимая"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Тестовая БД - SQLite в памяти
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
TestBase = declarative_base()