from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "new"


class TaskCreate(TaskBase):
    finish_time: Optional[datetime] = None

    @validator("title")
    def title_is_empty(cls, v):
        if len(v) == 0:
            raise ValueError("Title is empty")
        return v.title()

    @validator("status")
    def invalid_status(cls, v):
        if v not in ("new", "planned", "in progress", "finished"):
            raise ValueError("Status is invalid")
        return v.title()


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
