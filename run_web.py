#!/usr/bin/env python3
"""
웹 애플리케이션 실행 스크립트

물류 관리 시스템 웹 버전을 실행합니다.
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    try:
        import uvicorn
        from app.ui.web_app import app
        
        print("=" * 60)
        print("물류 관리 시스템 - 웹 애플리케이션")
        print("=" * 60)
        print()
        print("서버 시작 중...")
        print("접속 주소: http://localhost:8000")
        print("종료하려면 Ctrl+C를 누르세요.")
        print()
        print("=" * 60)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except ImportError as e:
        print("=" * 60)
        print("오류: 필요한 패키지가 설치되지 않았습니다.")
        print("=" * 60)
        print()
        print("다음 명령어로 필요한 패키지를 설치하세요:")
        print()
        print("  pip install fastapi uvicorn jinja2")
        print()
        print("또는:")
        print()
        print("  pip install -r requirements.txt")
        print()
        print("=" * 60)
        sys.exit(1)
        
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("서버를 종료합니다.")
        print("=" * 60)
        sys.exit(0)
        
    except Exception as e:
        print("=" * 60)
        print(f"오류가 발생했습니다: {e}")
        print("=" * 60)
        logging.exception("서버 실행 중 오류 발생")
        sys.exit(1)

