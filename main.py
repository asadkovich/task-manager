from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from services import users, services
from database import models, crud
from database.db import SessionLocal, engine
from database.schemas import UserCreate, TaskCreate, User

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

TOKEN_EXPIRE = 30


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.put("/task/create")
def create_task(task: TaskCreate, user: User = Depends(users.get_current_user), db: Session = Depends(get_db)):
    """Создаёт новую задачу, либо возвращает ошибку:
        400, если данные задачи некорректны
        500, если возникла проблема при сохранении
    """
    validation = services.validate_task(task)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["detail"],
            headers={"WWW-Authenticate": "Bearer"}
        )

    task = users.create_task(db, task, user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while saving task",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"status_code": status.HTTP_201_CREATED}


@app.put("/task/update")
def update_task(task_id: int,
                task: TaskCreate,
                user: User = Depends(users.get_current_user),
                db: Session = Depends(get_db)):
    """Обновляет поля задачи, либо возвращает ошибку:
        404, если задача не найдена
        400, если данные задачи некорректны
    """
    validation = services.validate_task(task)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["detail"],
            headers={"WWW-Authenticate": "Bearer"}
        )

    result = crud.update_task(db, task_id, task)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"status_code": status.HTTP_200_OK}


@app.post("/task/history")
def get_task_history(task_id: int, user: User = Depends(users.get_current_user), db: Session = Depends(get_db)):
    """Возвращает историю изменений задачи"""
    return crud.get_history(db, task_id)


@app.delete("/task/delete")
def delete_task(task_id: int, user: User = Depends(users.get_current_user), db: Session = Depends(get_db)):
    """Удаляет задачу по её id, либо возвращает 404, если задача не найдена"""
    result = crud.delete_task(db, task_id=task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"status_code": status.HTTP_200_OK}


@app.post("/user/tasks")
def read_tasks(db: Session = Depends(get_db), user: User = Depends(users.get_current_user)):
    """Возвращает все задачи для текущего пользователя"""
    return crud.get_tasks(db, user.id)


@app.post("/user/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Создаёт нового пользователя"""
    return users.perform_registration(db, user)


@app.post("/login")
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """Авторизирует пользователя и возвращает токен, либо возвращает ошибку 401"""
    user = users.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=TOKEN_EXPIRE)
    access_token = users.create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
