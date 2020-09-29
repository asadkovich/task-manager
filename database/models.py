from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    creation_time = Column(DateTime)
    finish_time = Column(DateTime, nullable=True, default=None)
    status = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))


class Change(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    creation_time = Column(DateTime)
    finish_time = Column(DateTime, nullable=True, default=None)
    status = Column(String)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
