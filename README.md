# task-manager
FastApi based task manger

### Перменные окружения:
```
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
SECRET_KEY
```
Расположить в файле .env в корне проекта

### Запуск:
```
docker-compose up --build
```
### Документация и использвание: http://127.0.0.1:8000/docs

### Функциональность:
```/task/create```  - создание задачи<br>
```/task/update```  - обновление данных о задаче<br>
```/task/history``` - история изменений задачи<br>
```/task/delete```  - удаление задачи по её id<br>
```/user/tasks```   - все задачи<br>
```/user/create```  - создание нового пользователя<br>
```/login```        - авторизация пользователя и получение токена<br>
