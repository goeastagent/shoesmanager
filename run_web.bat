@echo off
REM 웹 애플리케이션 실행 스크립트 (Windows)

echo ============================================================
echo 물류 관리 시스템 - 웹 애플리케이션
echo ============================================================
echo.

REM 가상환경 활성화
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo 오류: 가상환경을 찾을 수 없습니다.
    echo 먼저 setup_new_environment.bat을 실행하세요.
    pause
    exit /b 1
)

REM Python으로 웹 애플리케이션 실행
python run_web.py

pause

