import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(db, username: str, password: str, email: str, role: str = "user"):
    if db.users.find_one({"username": username}):
        return {"error": "Użytkownik już istnieje."}
    db.users.insert_one({
        "username": username,
        "password": hash_password(password),
        "email": email,
        "role": role
    })
    return {"message": "Użytkownik utworzony."}

def delete_user(db, username: str):
    result = db.users.delete_one({"username": username})
    if result.deleted_count == 0:
        return {"error": "Użytkownik nie istnieje."}
    return {"message": "Użytkownik usunięty."}

def verify_user(db, username: str, password: str) -> bool:
    user = db.users.find_one({"username": username})
    if not user:
        return False
    return user["password"] == hash_password(password)

def get_user_role(db, username: str):
    user = db.users.find_one({"username": username})
    return user.get("role") if user else None

def change_password(db, username: str, new_password: str):
    result = db.users.update_one({"username": username}, {"$set": {"password": hash_password(new_password)}})
    if result.modified_count == 0:
        return {"error": "Nie udało się zmienić hasła."}
    return {"message": "Hasło zmienione pomyślnie."}
