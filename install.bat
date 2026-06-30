@echo off
setlocal

echo Downloading install.py...
curl -L -o install_tmp.py https://raw.githubusercontent.com/Faticc/java8to25/refs/heads/main/install.py

if %errorlevel% neq 0 (
    echo Failed to download install.py
    exit /b 1
)

echo Running install.py...
python install_tmp.py

echo Cleaning up...
del install_tmp.py

echo Done.
