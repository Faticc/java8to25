import os
import sys
import json
import getpass
import subprocess
import urllib.request
from pathlib import Path


# ---------------------------------------------------------
# 0. Универсальная функция ввода с возможностью выхода
# ---------------------------------------------------------

def ask_input(prompt, cast=None):
    while True:
        value = input(prompt).strip()

        if value.lower() in ("exit", "выход", "quit", "q"):
            print("Выход из программы...")
            sys.exit(0)

        if cast:
            try:
                return cast(value)
            except ValueError:
                print("Ошибка: неверный формат. Попробуйте снова.")
        else:
            return value

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

RAM = ask_input("Введите общее количество оперативной памяти (в ГБ): ", int)
COUNT_CLIENTS = ask_input("Введите количество клиентов: ", int)

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
    name = ask_input(f"Введите имя аккаунта {i+1}: ")
    password = getpass.getpass(f"Введите пароль для аккаунта {name}: ")
    config["accounts"][name] = password

# ---------------------------------------------------------
# 4. Выбор клиента
# ---------------------------------------------------------

print("\n--- Выберите клиент ---")
for key, val in clients.items():
    print(f"{key}. {val}")

choice = ask_input("Введите номер клиента (1-3): ")
client = clients.get(choice)

if not client:
    print("Ошибка: неверный номер клиента.")
    sys.exit(1)

client_path = base_dir / "clients" / client
print(f"\nВыбран клиент: {client}")
print(f"Путь: {client_path}")

# ---------------------------------------------------------
# 5. Проверка существования клиента
# ---------------------------------------------------------

if not client_path.exists():
    print("Клиент не найден.")
    sys.exit(1)

# ---------------------------------------------------------
# 6. Сохранение config.json
# ---------------------------------------------------------

config_path = client_path / "config.json"
print("Создаю или перезаписываю config.json...")

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print("config.json готов!")

# ---------------------------------------------------------
# 7. Создание venv
# ---------------------------------------------------------

venv_path = client_path / "venv"
if not venv_path.exists():
    print("Создаю виртуальное окружение...")
    subprocess.run(["python", "-m", "venv", str(venv_path)], check=True)
    print("venv создан!")
else:
    print("venv уже существует — пропускаю.")

pip_path = venv_path / "Scripts" / "pip.exe"
python_path = venv_path / "Scripts" / "python.exe"

# ---------------------------------------------------------
# 8. Скачивание play.py
# ---------------------------------------------------------

play_url = "https://raw.githubusercontent.com/Faticc/java8to25/refs/heads/main/play.py"
play_path = client_path / "play.py"

if not play_path.exists():
    print("Скачиваю play.py...")
    urllib.request.urlretrieve(play_url, play_path)
    print("play.py скачан!")
else:
    print("play.py уже существует — пропускаю.")

# ---------------------------------------------------------
# 9. Скачивание requirements.txt
# ---------------------------------------------------------

req_url = "https://raw.githubusercontent.com/Faticc/java8to25/refs/heads/main/requirements.txt"
req_path = client_path / "requirements.txt"

if not req_path.exists():
    print("Скачиваю requirements.txt...")
    urllib.request.urlretrieve(req_url, req_path)
    print("requirements.txt скачан!")
else:
    print("requirements.txt уже существует — пропускаю.")

# ---------------------------------------------------------
# 10. Установка зависимостей
# ---------------------------------------------------------

print("Проверяю зависимости...")
subprocess.run([str(pip_path), "install", "-r", str(req_path)], check=True)
os.remove(req_path)
print("Зависимости установлены!")

# ---------------------------------------------------------
# 11. Создание run.bat
# ---------------------------------------------------------

run_bat_path = client_path / "run.bat"

if not run_bat_path.exists():
    print("Создаю run.bat...")
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
    print("run.bat создан!")
else:
    print("run.bat уже существует — пропускаю.")

# ---------------------------------------------------------
# 12. Создание ярлыка
# ---------------------------------------------------------

desktop = Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))
shortcut_path = desktop / f"{client}.lnk"

if shortcut_path.exists():
    print("Ярлык уже существует — пропускаю.")
else:
    print("Создаю ярлык на рабочем столе...")

    vbs_path = client_path / "create_shortcut.vbs"

    vbs_content = f'''
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{run_bat_path}"
    oLink.WorkingDirectory = "{client_path}"
    oLink.IconLocation = "{run_bat_path}"
    oLink.Save
    '''

    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(vbs_content)

    subprocess.run(["wscript.exe", str(vbs_path)], check=True)
    os.remove(vbs_path)

    print("Ярлык создан!")

# ---------------------------------------------------------
# 13. Завершение
# ---------------------------------------------------------

print("\nУстановка завершена! Клиент полностью готов к запуску.")
