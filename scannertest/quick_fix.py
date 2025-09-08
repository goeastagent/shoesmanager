#!/usr/bin/env python3
"""
USB 바코드 스캐너 빠른 수정 도구
- 실시간 입력 모니터링
- 스캐너 연결 상태 확인
- 자동 문제 진단
"""

import sys
import time
import threading
from datetime import datetime

def test_scanner_connection():
    """스캐너 연결 테스트"""
    print("🔍 USB 바코드 스캐너 연결 테스트")
    print("=" * 50)
    print("📋 테스트 방법:")
    print("   1. USB 바코드 스캐너를 연결하세요")
    print("   2. 바코드를 스캔하거나 키보드로 'test123'을 입력하세요")
    print("   3. 10초 안에 입력이 없으면 자동으로 종료됩니다")
    print("   4. Ctrl+C로 언제든 종료 가능")
    print("-" * 50)
    
    start_time = time.time()
    timeout = 10  # 10초 타임아웃
    
    try:
        while time.time() - start_time < timeout:
            try:
                # 비블로킹 입력 시도
                import select
                if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                    user_input = input()
                    if user_input:
                        print(f"\n✅ 입력 감지됨: '{user_input}'")
                        print(f"   길이: {len(user_input)} 문자")
                        print(f"   시간: {datetime.now().strftime('%H:%M:%S')}")
                        
                        # 바코드 형식 분석
                        if user_input.isdigit():
                            print("   형식: 숫자 바코드")
                        elif user_input.isalnum():
                            print("   형식: 영숫자 바코드")
                        else:
                            print("   형식: 혼합 문자")
                        
                        print("\n🎉 스캐너가 정상적으로 작동합니다!")
                        return True
                        
            except KeyboardInterrupt:
                print("\n\n프로그램을 종료합니다.")
                return False
            except EOFError:
                print("\n입력이 종료되었습니다.")
                return False
                
    except ImportError:
        # Windows에서는 select 모듈이 다를 수 있음
        print("⚠️  select 모듈을 사용할 수 없습니다. 기본 모드로 실행합니다.")
        try:
            user_input = input("바코드를 스캔하거나 텍스트를 입력하세요: ")
            if user_input:
                print(f"✅ 입력 감지됨: '{user_input}'")
                return True
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            return False
    
    print(f"\n⏰ {timeout}초 동안 입력이 없었습니다.")
    print("❌ 스캐너가 연결되지 않았거나 작동하지 않습니다.")
    return False

def show_troubleshooting_tips():
    """문제 해결 팁 표시"""
    print("\n🛠️  문제 해결 팁:")
    print("   1. USB 케이블이 제대로 연결되어 있는지 확인")
    print("   2. 스캐너 전원이 켜져 있는지 확인")
    print("   3. 다른 USB 포트로 시도")
    print("   4. 스캐너가 HID 키보드 모드로 설정되어 있는지 확인")
    print("   5. 시스템 환경설정 > 보안 및 개인정보 보호 > 입력 모니터링에서 터미널 권한 허용")
    print("   6. 터미널을 관리자 권한으로 실행: sudo python scannertest/quick_fix.py")

def main():
    """메인 함수"""
    print("🚀 USB 바코드 스캐너 빠른 수정 도구")
    print("=" * 60)
    
    # 스캐너 연결 테스트
    success = test_scanner_connection()
    
    if not success:
        show_troubleshooting_tips()
        
        # 추가 진단 옵션
        print("\n🔧 추가 진단을 원하시면:")
        print("   python scannertest/scanner_diagnostic.py")
        print("   python scannertest/barcode_scanner_test.py")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
