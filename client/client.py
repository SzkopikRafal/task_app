import requests

API_URL = "http://server:8000"

def main_menu():
    while True:
        print("\n=== MENU ===")
        print("1. Zaloguj się jako klient")
        print("2. Zaloguj się jako administrator")
        print("0. Wyjdź")
        choice = input("Wybierz opcję: ")

        if choice == "1":
            client_menu()
        elif choice == "2":
            admin_menu()
        elif choice == "0":
            break


def client_menu():
    username = input("Login: ")
    password = input("Hasło: ")

    res = requests.post(f"{API_URL}/auth/login", params={"user": username, "password": password})
    if res.status_code != 200:
        print(res.json()["detail"])
        return

    while True:
        print("\n=== KLIENT ===")
        print("1. Dodaj zadanie")
        print("2. Pokaż moje zadania")
        print("3. Usuń zadanie")
        print("4. Zmień hasło")
        print("0. Wyloguj")
        choice = input("Wybierz opcję: ")

        if choice == "1":
            description = input("Opis zadania: ")
            datetime = input("Data i godzina (np. 2025-04-01 13:48): ")
            payload = {"user": username, "password": password, "description": description, "datetime": datetime}
            res = requests.post(f"{API_URL}/task/add", json=payload)
            print(res.json())
        elif choice == "2":
            res = requests.post(f"{API_URL}/task/list", json={"user": username, "password": password})
            tasks = res.json().get("tasks", [])
            if not tasks:
                print("Brak zadań.")
            for t in tasks:
                print(f"- {t['datetime']}: {t['description']}")
        elif choice == "3":
            desc = input("Dokładny opis zadania do usunięcia: ")
            res = requests.post(f"{API_URL}/task/delete", json={"user": username, "password": password, "description": desc})
            print(res.json())
        elif choice == "4":
            new_pass = input("Nowe hasło: ")
            res = requests.post(f"{API_URL}/auth/change-password", json={
                "user": username,
                "old_password": password,
                "new_password": new_pass
            })
            print(res.json())
            if res.status_code == 200:
                password = new_pass
        elif choice == "0":
            break


def admin_menu():
    admin_user = input("Login administratora: ")
    admin_pass = input("Hasło administratora: ")

    res = requests.post(f"{API_URL}/auth/login", params={"user": admin_user, "password": admin_pass})
    if res.status_code != 200:
        print(res.json()["detail"])
        return

    while True:
        print("\n=== ADMIN ===")
        print("1. Dodaj użytkownika")
        print("2. Usuń użytkownika")
        print("3. Zmień swoje hasło")
        print("0. Wyloguj")
        choice = input("Wybierz opcję: ")

        if choice == "1":
            username = input("Nowa nazwa użytkownika: ")
            password = input("Hasło: ")
            email = input("Email użytkownika: ")
            res = requests.post(f"{API_URL}/admin/create",
                                params={"username": username, "password": password, "email": email,
                                        "admin_user": admin_user, "admin_pass": admin_pass})
            print(res.json())
        elif choice == "2":
            username = input("Nazwa użytkownika do usunięcia: ")
            res = requests.post(f"{API_URL}/admin/delete",
                                params={"username": username,
                                        "admin_user": admin_user, "admin_pass": admin_pass})
            print(res.json())
        elif choice == "3":
            new_pass = input("Nowe hasło administratora: ")
            res = requests.post(f"{API_URL}/auth/change-password", json={
                "user": admin_user,
                "old_password": admin_pass,
                "new_password": new_pass
            })
            print(res.json())
            if res.status_code == 200:
                admin_pass = new_pass
        elif choice == "0":
            break


if __name__ == "__main__":
    main_menu()
