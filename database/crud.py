from datetime import datetime

from sqlalchemy.orm import Session

from . import models, schemas
from auth import services


def get_user(db: Session, login: str):
    return db.query(models.User).filter(models.User.login == login).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = services.get_password_hash(user.password)

    db_user = models.User(login=user.login, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return user


def get_tasks(db: Session, user_id: int):
    return db.query(models.Task).filter(models.Task.user_id == user_id).all()


def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(title=task.title,
                          description=task.description,
                          creation_time=datetime.now(),
                          status="new",
                          user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return task


def update_task(db: Session, task: schemas.TaskCreate):
    db_task = db.query(models.Task).filter(models.Task.id == task.id)
    if not db_task.first():
        return False

    _save_task_changes(db, db_task.first())
    db_task.update(task)
    db.commit()

    return True


def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()

    return True


def get_history(db: Session, task_id: int):
    return db.query(models.Change).filter(models.Change.task_id == task_id).all()


def _save_task_changes(db: Session, task: schemas.Task):
    db_change = models.Change(title=task.title,
                              description=task.description,
                              creation_time=task.creation_time,
                              status=task.status,
                              task_id=task.id)
    db.add(db_change)
    db.commit()
    db.refresh(db_change)
