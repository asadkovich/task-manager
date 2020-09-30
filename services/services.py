from datetime import datetime
from passlib.context import CryptContext

from database.schemas import TaskCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_task(task: TaskCreate) -> dict:
    if len(task.title) == 0:
        return {"valid": False, "detail": "Title is empty"}
    if task.status not in ("new", "planned", "in progress", "finished"):
        return {"valid": False, "detail": "Invalid status, should be: new, planned, in progress or finished"}

    return {"valid": True}


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
