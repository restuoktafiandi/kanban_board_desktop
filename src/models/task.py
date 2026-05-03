from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from config.db import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='Backlog')
    tags = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    due_date = Column(DateTime, nullable=True)