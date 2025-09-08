#!/usr/bin/env python3
"""
USB 바코드 스캐너 진단 도구
- 키보드 입력 모니터링
- 스캐너 연결 상태 확인
- 입력 패턴 분석
"""

import sys
import time
import threading
from datetime import datetime
import select
import tty
import termios

class ScannerDiagnostic:
    def __init__(self):
        self.input_buffer = ""
        self.scan_count = 0
        self.start_time = time.time()
        self.last_input_time = None
        
    def setup_terminal(self):
        """터미널을 raw 모드로 설정"""
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
        
    def restore_terminal(self):
        """터미널 설정 복원"""
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        
    def get_input_with_timeout(self, timeout=1):
        """타임아웃이 있는 입력 받기"""
        if select.select([sys.stdin], [], [], timeout)[0]:
            return sys.stdin.read(1)
        return None
        
    def analyze_input_pattern(self, char):
        """입력 패턴 분석"""
        now = time.time()
        
        if self.last_input_time:
            time_diff = now - self.last_input_time
            if time_diff < 0.1:  # 100ms 이내 연속 입력
                return "fast_scan"
            elif time_diff > 2.0:  # 2초 이상 간격
                return "manual_type"
        
        self.last_input_time = now
        return "normal"
        
    def run_diagnostic(self):
        """진단 실행"""
        print("🔍 USB 바코드 스캐너 진단 도구")
        print("=" * 50)
        print("📋 사용법:")
        print("   1. USB 바코드 스캐너를 연결하세요")
        print("   2. 바코드를 스캔하거나 키보드로 텍스트를 입력하세요")
        print("   3. 'quit'를 입력하면 종료됩니다")
        print("   4. Ctrl+C로 강제 종료")
        print("-" * 50)
        
        self.setup_terminal()
        
        try:
            while True:
                char = self.get_input_with_timeout(0.1)
                
                if char is None:
                    continue
                    
                # 종료 조건
                if char == '\x03':  # Ctrl+C
                    print("\n\n프로그램을 종료합니다.")
                    break
                    
                # 엔터키 처리
                if char == '\r' or char == '\n':
                    if self.input_buffer.strip().lower() == 'quit':
                        print("\n\n프로그램을 종료합니다.")
                        break
                    
                    if self.input_buffer.strip():
                        self.process_complete_input()
                    continue
                
                # 백스페이스 처리
                if char == '\x7f' or char == '\b':
                    if self.input_buffer:
                        self.input_buffer = self.input_buffer[:-1]
                        print('\b \b', end='', flush=True)
                    continue
                
                # 일반 문자 처리
                self.input_buffer += char
                pattern = self.analyze_input_pattern(char)
                
                # 실시간 표시
                print(char, end='', flush=True)
                
                # 패턴별 처리
                if pattern == "fast_scan":
                    print(f" [빠른스캔]", end='', flush=True)
                elif pattern == "manual_type":
                    print(f" [수동입력]", end='', flush=True)
                    
        except KeyboardInterrupt:
            print("\n\n프로그램을 강제 종료합니다.")
        finally:
            self.restore_terminal()
            
    def process_complete_input(self):
        """완전한 입력 처리"""
        input_text = self.input_buffer.strip()
        if not input_text:
            return
            
        self.scan_count += 1
        current_time = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n\n📱 입력 #{self.scan_count} [{current_time}]")
        print(f"   내용: '{input_text}'")
        print(f"   길이: {len(input_text)} 문자")
        
        # 바코드 형식 분석
        if input_text.isdigit():
            print(f"   형식: 숫자 바코드")
        elif input_text.isalnum():
            print(f"   형식: 영숫자 바코드")
        else:
            print(f"   형식: 혼합 문자")
            
        # 입력 속도 분석
        if self.last_input_time:
            total_time = time.time() - self.start_time
            avg_speed = len(input_text) / max(total_time, 0.1)
            print(f"   입력속도: {avg_speed:.1f} 문자/초")
        
        print("-" * 30)
        
        # 버퍼 초기화
        self.input_buffer = ""

def main():
    """메인 함수"""
    print("🚀 USB 바코드 스캐너 진단 도구 v1.0")
    print("=" * 60)
    
    diagnostic = ScannerDiagnostic()
    
    try:
        diagnostic.run_diagnostic()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return 1
    
    print("\n✅ 진단이 완료되었습니다.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
