@echo off
chcp 65001 >nul
echo ========================================
echo    Shoes Management System Build Script
echo ========================================
echo.

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
