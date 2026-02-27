from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Department(Base):
    """""Модель подразделения"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Отношения
    children = relationship("Department", back_populates="parent")
    employees = relationship("Employee", back_populates="department", cascade="all, delete-orphan")

    # Ограничения
    __table_args__ = (
        UniqueConstraint('name', 'parent_id', name='uq_department_name_parent'),
        CheckConstraint('id != parent_id', name='check_no_self_reference'),
    )

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"