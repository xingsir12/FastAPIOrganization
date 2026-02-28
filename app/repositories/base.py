"""Базовый репозиторий для работы с БД"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from app.database import Base

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Базовый класс репозитория с общими методами CRUD"""
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Args:
            model: SQLAlchemy модель (должна наследоваться от Base)
            db: Сессия базы данных
        """

        if not issubclass(model, Base):
            raise TypeError(f"Model must be subclass of Base, got {model}")
            
        self.model = model
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получить объект по ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить все объекты с пагинацией"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, **kwargs) -> ModelType:
        """Создать новый объект из kwargs"""
        obj = self.model(**kwargs)
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception as e:
            self.db.rollback()
            raise
    
    def create_from_obj(self, obj: ModelType) -> ModelType:
        """Создать новый объект (альтернативный метод)"""
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception as e:
            self.db.rollback()
            raise
    
    def update(self, obj: ModelType, **kwargs) -> ModelType:
        """Обновить объект с новыми данными"""
        try:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except Exception as e:
            self.db.rollback()
            raise
    
    def delete(self, obj: ModelType) -> None:
        """Удалить объект"""
        try:
            self.db.delete(obj)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise
    
    def exists(self, id: int) -> bool:
        """Проверить существование объекта по ID"""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None