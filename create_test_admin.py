from pymongo import MongoClient
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

client = MongoClient("mongodb://localhost:27017/")
db = client["task_db"]

admin_username = "admin"
admin_password = "admin123"
admin_hashed = hash_password(admin_password)

if db.users.find_one({"username": admin_username}):
    print("Admin już istnieje.")
else:
    db.users.insert_one({
        "username": admin_username,
        "password": admin_hashed,
        "role": "admin"
    })
    print("Testowy administrator dodany!")
