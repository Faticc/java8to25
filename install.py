import os
import json
import getpass
import subprocess
import urllib.request
from pathlib import Path

# ---------------------------------------------------------
# 1. Базовые параметры
# ---------------------------------------------------------

user = getpass.getuser()
base_dir = Path(f"C:/Users/{user}/McSkill")

clients = {
    "1": "Galaxy_1.7.10",
    "2": "Industrial_1.7.10",
    "3": "TechnoMagic_1.7.10"
}

# ---------------------------------------------------------
# 2. Ввод параметров
# ---------------------------------------------------------

def ask_int(prompt):
    try:
        return int(input(prompt))
    except ValueError:
        print("Ошибка: нужно целое число.")
        exit(1)

RAM = ask_int("Введите общее количество оперативной памяти (в ГБ): ")
COUNT_CLIENTS = ask_int("Введите количество клиентов: ")

# ---------------------------------------------------------
# 3. Формирование config.json
# ---------------------------------------------------------

config = {
    "__comment__path": "Пути к клиенту",
    "java_path": str(base_dir / "java" / "25-temurin" / "bin" / "java.exe"),
    "asset_dir": str(base_dir / "assets" / "assets1.7.10"),

    "__comment__ram": "Общее количество оперативной памяти, выделяемое для всех клиентов.",
    "total_ram_mb": RAM * 1024,

    "__comment__accounts": "Аккаунты указываются в формате: имя_аккаунта:пароль.",
    "accounts": {}
}

for i in range(COUNT_CLIENTS):
    name = input(f"Введите имя аккаунта {i+1}: ")
    password = getpass.getpass(f"Введите пароль для аккаунта {name}: ")
    config["accounts"][name] = password

# ---------------------------------------------------------
# 4. Выбор клиента
# ---------------------------------------------------------

print("\n--- Выберите клиент ---")
for key, val in clients.items():
    print(f"{key}. {val}")

choice = input("Введите номер клиента (1-3): ")
client = clients.get(choice)

if not client:
    print("Ошибка: неверный номер клиента.")
    exit(1)

client_path = base_dir / "clients" / client
print(f"\nВыбран клиент: {client}")
print(f"Путь: {client_path}")

# ---------------------------------------------------------
# 5. Сохранение config.json
# ---------------------------------------------------------

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print("✔ Конфигурационный файл успешно создан!")

# ---------------------------------------------------------
# 6. Создание venv
# ---------------------------------------------------------

venv_path = client_path / "venv"
print("\nСоздаю виртуальное окружение...")

subprocess.run(["python", "-m", "venv", str(venv_path)], check=True)
pip_path = venv_path / "Scripts" / "pip.exe"
python_path = venv_path / "Scripts" / "python.exe"

print("✔ venv создан!")

# ---------------------------------------------------------
# 7. Скачивание play.py
# ---------------------------------------------------------

play_url = "https://raw.githubusercontent.com/Faticc/java8to25/refs/heads/main/play.py"
play_path = client_path / "play.py"

print("Скачиваю play.py...")
urllib.request.urlretrieve(play_url, play_path)
print("✔ play.py скачан!")

# ---------------------------------------------------------
# 8. Установка зависимостей
# ---------------------------------------------------------

req_url = "https://raw.githubusercontent.com/Faticc/java8to25/blob/main/requirements.txt"
req_path = client_path / "requirements.txt"

print("Скачиваю requirements.txt...")
urllib.request.urlretrieve(req_url, req_path)
print("✔ requirements.txt скачан!")

print("Устанавливаю зависимости...")
subprocess.run([str(pip_path), "install", "-r", str(req_path)], check=True)
print("✔ Зависимости установлены!")

# ---------------------------------------------------------
# 9. Создание run.bat
# ---------------------------------------------------------

run_bat_path = client_path / "run.bat"

run_bat_content = """@echo off
chcp 65001 >nul
title Running Client...

cd /d "%~dp0"
call "venv\\Scripts\\activate.bat"

python play.py
pause
"""

with open(run_bat_path, "w", encoding="utf-8") as f:
    f.write(run_bat_content)

print("✔ run.bat создан!")

# ---------------------------------------------------------
# 10. Завершение
# ---------------------------------------------------------

print("\nУстановка завершена! Клиент полностью готов к запуску.")
