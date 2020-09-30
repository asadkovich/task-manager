from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "new"


class TaskCreate(TaskBase):
    finish_time: Optional[datetime] = None


class Task(TaskBase):
    id: int
    creation_time: datetime
    user_id: int

    class Config:
        orm_mode = True


class TaskChange(Task):
    task_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    tasks: List[Task] = []

    class Config:
        orm_mode = True
