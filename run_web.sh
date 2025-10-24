#!/bin/bash
# 웹 애플리케이션 실행 스크립트 (macOS/Linux)

echo "============================================================"
echo "물류 관리 시스템 - 웹 애플리케이션"
echo "============================================================"
echo

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

# 가상환경 활성화
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
else
    echo "오류: 가상환경을 찾을 수 없습니다."
    echo "먼저 가상환경을 설정하세요:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Python으로 웹 애플리케이션 실행
python run_web.py

