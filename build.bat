@echo off
chcp 65001 >nul
echo ========================================
echo    Shoes Management System Build Script
echo ========================================
echo.

REM Check if virtual environment exists, create if not
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating new virtual environment...
    echo.
    
    REM Create virtual environment
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        echo Please check your Python installation.
        pause
        exit /b 1
    )
    
    echo Virtual environment created successfully.
    echo Installing dependencies...
    
    REM Activate and install dependencies
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        echo Please check requirements.txt file.
        pause
        exit /b 1
    )
    
    echo Dependencies installed successfully.
    echo.
) else (
    echo Virtual environment found.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run Python build script
echo Running build script...
python build_windows.py

REM Pause after build completion
echo.
echo Build completed.
pause
