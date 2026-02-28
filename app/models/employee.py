from sqlalchemy import Column, Date, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class Employee(Base):
    """Модель сотрудника"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(
        Integer, 
        ForeignKey("departments.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    full_name = Column(String(200), nullable=False, index=True)
    position = Column(String(200), nullable=False, index=True) 
    hired_at = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Отношения
    department = relationship("Department", back_populates="employees")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, full_name='{self.full_name}', position='{self.position}')>"