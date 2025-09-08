#!/usr/bin/env python3
"""
USB 바코드 스캐너 테스트 프로그램
- 다양한 바코드 형식 지원
- 실시간 입력 모니터링
- 에러 처리 및 로깅
"""

import sys
import time
import threading
from datetime import datetime
import json

class BarcodeScanner:
    def __init__(self):
        self.scan_count = 0
        self.scan_history = []
        self.running = True
        
    def log_scan(self, barcode):
        """바코드 스캔 로그 기록"""
        scan_data = {
            'timestamp': datetime.now().isoformat(),
            'barcode': barcode,
            'length': len(barcode),
            'scan_number': self.scan_count + 1
        }
        self.scan_history.append(scan_data)
        self.scan_count += 1
        return scan_data
    
    def display_scan_info(self, scan_data):
        """스캔된 바코드 정보 표시"""
        print(f"\n{'='*60}")
        print(f"📱 바코드 스캔 #{scan_data['scan_number']}")
        print(f"⏰ 시간: {scan_data['timestamp']}")
        print(f"🏷️  바코드: {scan_data['barcode']}")
        print(f"📏 길이: {scan_data['length']} 문자")
        
        # 바코드 형식 분석
        barcode = scan_data['barcode']
        if barcode.isdigit():
            print(f"📊 형식: 숫자 바코드")
        elif barcode.isalnum():
            print(f"📊 형식: 영숫자 바코드")
        else:
            print(f"📊 형식: 혼합 문자 바코드")
            
        print(f"{'='*60}")
    
    def start_scanning(self):
        """바코드 스캔 시작"""
        print("🔍 USB 바코드 스캐너 테스트 시작")
        print("📋 사용법:")
        print("   - 바코드를 스캔하세요")
        print("   - 각 스캔 후 자동으로 결과가 표시됩니다")
        print("   - 종료하려면 Ctrl+C를 누르세요")
        print("   - 'stats'를 입력하면 통계를 볼 수 있습니다")
        print("   - 'history'를 입력하면 스캔 기록을 볼 수 있습니다")
        print("   - 'clear'를 입력하면 기록을 지울 수 있습니다")
        print("-" * 60)
        
        try:
            while self.running:
                try:
                    # 사용자 입력 대기
                    user_input = input("바코드를 스캔하거나 명령어를 입력하세요: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # 특별 명령어 처리
                    if user_input.lower() == 'stats':
                        self.show_stats()
                        continue
                    elif user_input.lower() == 'history':
                        self.show_history()
                        continue
                    elif user_input.lower() == 'clear':
                        self.clear_history()
                        continue
                    elif user_input.lower() in ['quit', 'exit', 'q']:
                        print("프로그램을 종료합니다.")
                        break
                    
                    # 바코드 스캔 처리
                    scan_data = self.log_scan(user_input)
                    self.display_scan_info(scan_data)
                    
                except EOFError:
                    print("\n입력이 종료되었습니다.")
                    break
                except KeyboardInterrupt:
                    print("\n\n프로그램을 종료합니다.")
                    break
                    
        except Exception as e:
            print(f"❌ 에러가 발생했습니다: {e}")
            return False
        
        return True
    
    def show_stats(self):
        """스캔 통계 표시"""
        if not self.scan_history:
            print("📊 아직 스캔된 바코드가 없습니다.")
            return
        
        print(f"\n📊 스캔 통계")
        print(f"   총 스캔 횟수: {self.scan_count}")
        print(f"   평균 바코드 길이: {sum(s['length'] for s in self.scan_history) / len(self.scan_history):.1f}")
        
        # 가장 긴/짧은 바코드
        longest = max(self.scan_history, key=lambda x: x['length'])
        shortest = min(self.scan_history, key=lambda x: x['length'])
        print(f"   가장 긴 바코드: {longest['barcode']} ({longest['length']}자)")
        print(f"   가장 짧은 바코드: {shortest['barcode']} ({shortest['length']}자)")
    
    def show_history(self):
        """스캔 기록 표시"""
        if not self.scan_history:
            print("📋 스캔 기록이 없습니다.")
            return
        
        print(f"\n📋 스캔 기록 (최근 {min(10, len(self.scan_history))}개)")
        for scan in self.scan_history[-10:]:
            print(f"   #{scan['scan_number']}: {scan['barcode']} ({scan['timestamp']})")
    
    def clear_history(self):
        """스캔 기록 초기화"""
        self.scan_history.clear()
        self.scan_count = 0
        print("🗑️  스캔 기록이 초기화되었습니다.")

def main():
    """메인 함수"""
    print("🚀 USB 바코드 스캐너 테스트 프로그램 v1.0")
    print("=" * 60)
    
    scanner = BarcodeScanner()
    
    try:
        success = scanner.start_scanning()
        if success:
            print("\n✅ 프로그램이 정상적으로 종료되었습니다.")
        else:
            print("\n❌ 프로그램 실행 중 오류가 발생했습니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
