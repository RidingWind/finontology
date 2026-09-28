@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 setup.py
) else (
    python setup.py
)

if errorlevel 1 (
    echo.
    echo 运行失败。请确认已安装 Python 3.11~3.13 并勾选 "Add python.exe to PATH"。
    echo 官网：https://www.python.org/downloads/windows/
)

echo.
pause
