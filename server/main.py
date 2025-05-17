from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from pymongo import MongoClient
from users import create_user, delete_user, verify_user, get_user_role, change_password
from datetime import datetime

app = FastAPI()
client = MongoClient("mongodb://mongodb:27017/")
db = client["task_db"]
tasks = db["tasks"]

class Task(BaseModel):
    user: str
    password: str
    description: str
    datetime: str

    @validator("datetime")
    def validate_datetime(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M")
            return value
        except ValueError:
            raise ValueError("Niepoprawny format daty. Użyj YYYY-MM-DD HH:MM")

class Auth(BaseModel):
    user: str
    password: str

class PasswordChange(BaseModel):
    user: str
    old_password: str
    new_password: str

@app.post("/admin/create")
def admin_create(username: str, password: str, email: str, admin_user: str, admin_pass: str):
    if not verify_user(db, admin_user, admin_pass):
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane administratora.")
    if get_user_role(db, admin_user) != "admin":
        raise HTTPException(status_code=403, detail="Brak uprawnień administratora.")
    return create_user(db, username, password, email)

@app.post("/admin/delete")
def admin_delete(username: str, admin_user: str, admin_pass: str):
    if not verify_user(db, admin_user, admin_pass):
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane administratora.")
    if get_user_role(db, admin_user) != "admin":
        raise HTTPException(status_code=403, detail="Brak uprawnień administratora.")
    tasks.delete_many({"user": username})
    return delete_user(db, username)

@app.post("/task/add")
def add_task(task: Task):
    if not db.users.find_one({"username": task.user}):
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje.")
    if not verify_user(db, task.user, task.password):
        raise HTTPException(status_code=401, detail="Nieprawidłowe hasło.")
    tasks.insert_one(task.dict())
    return {"message": "Zadanie dodane pomyślnie"}

@app.post("/task/list")
def list_tasks(auth: Auth):
    if not verify_user(db, auth.user, auth.password):
        raise HTTPException(status_code=401, detail="Błędny login lub hasło.")
    user_tasks = list(tasks.find({"user": auth.user}, {"_id": 0}))
    try:
        sorted_tasks = sorted(user_tasks, key=lambda x: datetime.strptime(x["datetime"], "%Y-%m-%d %H:%M"))
    except:
        sorted_tasks = user_tasks
    return {"tasks": sorted_tasks}

@app.post("/task/delete")
def delete_task(task: Task):
    if not verify_user(db, task.user, task.password):
        raise HTTPException(status_code=401, detail="Błędny login lub hasło.")
    result = tasks.delete_one({"user": task.user, "description": task.description})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Nie znaleziono zadania.")
    return {"message": "Zadanie usunięte."}

@app.post("/auth/login")
def login(user: str, password: str):
    db_user = db.users.find_one({"username": user})
    if not db_user:
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje.")
    if not verify_user(db, user, password):
        raise HTTPException(status_code=401, detail="Nieprawidłowe hasło.")
    return {"message": "Zalogowano pomyślnie"}

@app.post("/auth/change-password")
def change_user_password(data: PasswordChange):
    if not verify_user(db, data.user, data.old_password):
        raise HTTPException(status_code=401, detail="Nieprawidłowe dane logowania.")
    return change_password(db, data.user, data.new_password)
