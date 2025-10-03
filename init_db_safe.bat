@echo off
REM Set console to UTF-8 for proper character display
chcp 65001 >nul

echo ==========================================
echo    Safe Database Initialization Script
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please create virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    echo Please check your Python installation.
    pause
    exit /b 1
)

REM Run safe database initialization script
echo Running safe database initialization...
python init_database_safe.py

REM Check initialization result
if errorlevel 1 (
    echo.
    echo ERROR: Database initialization failed!
    echo Please check the error messages above.
    echo.
    echo Troubleshooting tips:
    echo 1. Make sure all dependencies are installed: pip install -r requirements.txt
    echo 2. Check if you're running from the project root directory
    echo 3. Verify Python version compatibility
) else (
    echo.
    echo SUCCESS: Database initialized safely!
    echo You can now run the application or build the executable.
)

echo.
echo Press any key to exit...
pause >nul
