@echo off
REM Set console to UTF-8 for proper character display
chcp 65001 >nul

echo ==========================================
echo    Shoes Management System - Optimized Build
echo ==========================================
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

REM Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Run optimized build script
echo Running optimized build script...
python build_windows_optimized.py

REM Check build result
if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above.
) else (
    echo.
    echo SUCCESS: Build completed!
    echo Executable location: dist\ShoesManager.exe
)

echo.
echo Press any key to exit...
pause >nul
