import time
import smtplib
from email.mime.text import MIMEText
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from zoneinfo import ZoneInfo
from pymongo.errors import ServerSelectionTimeoutError

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

while True:
    try:
        client = MongoClient("mongodb://mongodb:27017/", serverSelectionTimeoutMS=5000)
        client.server_info()
        break
    except ServerSelectionTimeoutError:
        print("Oczekiwanie na MongoDB...")
        time.sleep(5)

db = client["task_db"]
tasks = db["tasks"]
users = db["users"]

sent_notifications = set()

def send_email(to_address, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_address

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

while True:
    now = datetime.now(ZoneInfo("Europe/Warsaw"))
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Sprawdzam zadania...")
    future_time = now + timedelta(minutes=10)

    for task in tasks.find():
        task_time = datetime.strptime(task["datetime"], "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("Europe/Warsaw"))

        if now <= task_time <= future_time:
            user = users.find_one({"username": task["user"]})
            if not user:
                continue

            email = user.get("email")
            if not email:
                continue

            unique_key = f"{task['_id']}_{task['user']}"

            if unique_key not in sent_notifications:
                subject = "[Przypomnienie] Twoje zadanie za 10 minut!"
                body = f"Cześć {task['user']},\n\nPrzypomnienie o zadaniu: {task['description']}\nCzas: {task['datetime']}\n\nPozdrawiamy!"
                try:
                    send_email(email, subject, body)
                    print(f"Wysłano powiadomienie do {email}")
                    sent_notifications.add(unique_key)
                except Exception as e:
                    print(f"Błąd wysyłki maila: {e}")

    time.sleep(60)