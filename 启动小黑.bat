@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Python environment not found: .venv\Scripts\python.exe
    echo Please create the virtual environment in this folder first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "罗小黑桌宠.py"
if errorlevel 1 (
    echo.
    echo Startup failed. Please copy or screenshot the error above.
    pause
)
endlocal