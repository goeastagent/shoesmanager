@echo off
REM Set console to UTF-8 for proper character display
chcp 65001 >nul

echo ==========================================
echo    New Environment Setup Script
echo ==========================================
echo.
echo This script will set up a completely new environment
echo for the Shoes Management System.
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ==========================================
    echo    Python Installation Required
    echo ==========================================
    echo.
    echo Python is not installed or not in PATH.
    echo.
    echo Please follow these steps:
    echo.
    echo 1. Download Python from: https://www.python.org/downloads/
    echo 2. During installation, make sure to check:
    echo    - "Add Python to PATH"
    echo    - "Install for all users" (recommended)
    echo.
    echo 3. After installation, restart this script.
    echo.
    echo Alternative: Try these commands in Command Prompt:
    echo   py --version
    echo   python3 --version
    echo   py -3 --version
    echo.
    echo If any of these work, you can use that command instead.
    echo.
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

REM Check if we're in the right directory
if not exist "app\ui\tk_app.py" (
    echo ERROR: Please run this script from the project root directory!
    echo Expected to find: app\ui\tk_app.py
    pause
    exit /b 1
)

echo Project structure verified.
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    echo Please check your Python installation.
    pause
    exit /b 1
)

echo Virtual environment created successfully.
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

echo Virtual environment activated.
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    echo Please check requirements.txt file.
    pause
    exit /b 1
)

echo Dependencies installed successfully.
echo.

REM Initialize database
echo Initializing database...
python init_database_safe.py
if errorlevel 1 (
    echo ERROR: Database initialization failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo    Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Run GUI: python -m app.ui.tk_app
echo 2. Run CLI: python -m app.ui.cli list
echo 3. Build executable: build_optimized.bat
echo.
echo Press any key to exit...
pause >nul
