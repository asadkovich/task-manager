from datetime import timedelta

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import users
from database import models, crud
from database.db import SessionLocal, engine
from database.schemas import UserCreate, TaskCreate, User, Task

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
    task = users.create_task(db, task, user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while saving task",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"status_code": status.HTTP_201_CREATED}


@app.put("/task/update")
def update_task(task: Task, user: User = Depends(users.get_current_user), db: Session = Depends(get_db)):
    result = crud.update_task(db, task)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"status_code": status.HTTP_200_OK}


@app.delete("/task/delete")
def delete_task(task_id: int, user: User = Depends(users.get_current_user), db: Session = Depends(get_db)):
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
    return crud.get_tasks(db, user.id)


@app.post("/user/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return users.perform_registration(db, user)


@app.post("/login")
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
