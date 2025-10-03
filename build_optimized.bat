@echo off
REM Set console to UTF-8 for proper character display
chcp 65001 >nul

echo ==========================================
echo    Shoes Management System - Optimized Build
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please create virtual environment first:
    echo python -m venv venv
    echo venv\Scripts\activate.bat
    echo pip install -r requirements.txt
    pause
    exit /b 1
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
