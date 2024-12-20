from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base # Предполагается, что Base определен в модуле database

class OuterTask(Base):
    __tablename__ = "outer_tasks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # Айдишник
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Айдишник пользователя
    title = Column(String, nullable=False)  # Название задачи
    status = Column(Boolean, default=False)  # Статус (выполнено или нет)
    
    # Связь с пользователем
    user = relationship("User", back_populates="tasks")  # Предполагается, что у User есть tasks
