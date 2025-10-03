@echo off
echo ========================================
echo    신발 관리 시스템 빌드 스크립트
echo ========================================
echo.

REM 가상환경 활성화
echo 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

REM Python 빌드 스크립트 실행
echo 빌드 스크립트를 실행합니다...
python build_windows.py

REM 빌드 완료 후 일시정지
echo.
echo 빌드가 완료되었습니다.
pause
