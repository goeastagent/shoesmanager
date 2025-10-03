@echo off
REM Set console to UTF-8 for proper character display
chcp 65001 >nul

echo ==========================================
echo    Advanced Environment Setup Script
echo ==========================================
echo.
echo This script will set up a completely new environment
echo for the Shoes Management System.
echo.

REM Function to find Python executable
set PYTHON_CMD=
echo Searching for Python installation...

REM Try different Python commands
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo Found: python
    goto :found_python
)

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    echo Found: py
    goto :found_python
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    echo Found: python3
    goto :found_python
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    echo Found: py -3
    goto :found_python
)

REM Try to find Python in common locations
if exist "C:\Python39\python.exe" (
    set PYTHON_CMD=C:\Python39\python.exe
    echo Found: C:\Python39\python.exe
    goto :found_python
)

if exist "C:\Python310\python.exe" (
    set PYTHON_CMD=C:\Python310\python.exe
    echo Found: C:\Python310\python.exe
    goto :found_python
)

if exist "C:\Python311\python.exe" (
    set PYTHON_CMD=C:\Python311\python.exe
    echo Found: C:\Python311\python.exe
    goto :found_python
)

if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    echo Found: C:\Python312\python.exe
    goto :found_python
)

if exist "C:\Python313\python.exe" (
    set PYTHON_CMD=C:\Python313\python.exe
    echo Found: C:\Python313\python.exe
    goto :found_python
)

REM Try AppData locations
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe
    echo Found: %USERPROFILE%\AppData\Local\Programs\Python\Python39\python.exe
    goto :found_python
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe
    echo Found: %USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe
    goto :found_python
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe
    echo Found: %USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe
    goto :found_python
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe
    echo Found: %USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe
    goto :found_python
)

if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe" (
    set PYTHON_CMD=%USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe
    echo Found: %USERPROFILE%\AppData\Local\Programs\Python\Python313\python.exe
    goto :found_python
)

REM If no Python found, show installation guide
echo.
echo ==========================================
echo    Python Installation Required
echo ==========================================
echo.
echo Python was not found in any common locations.
echo.
echo Please install Python by following these steps:
echo.
echo 1. Go to: https://www.python.org/downloads/
echo 2. Download the latest Python version
echo 3. During installation, make sure to check:
echo    - "Add Python to PATH" (IMPORTANT!)
echo    - "Install for all users" (recommended)
echo.
echo 4. After installation, restart Command Prompt and run this script again.
echo.
echo Alternative installation methods:
echo - Microsoft Store: Search for "Python" in Microsoft Store
echo - Anaconda: https://www.anaconda.com/products/distribution
echo.
pause
exit /b 1

:found_python
echo.
echo Using Python command: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

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
%PYTHON_CMD% -m venv venv
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
