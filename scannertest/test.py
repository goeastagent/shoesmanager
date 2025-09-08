import sys
import threading
import time

print("USB 바코드 스캐너 테스트를 시작합니다.")
print("바코드를 스캔하세요. (종료하려면 Ctrl+C)")
print("-" * 50)

def read_barcode():
    """바코드 스캐너 입력을 읽는 함수"""
    try:
        while True:
            # stdin에서 한 줄씩 읽기 (바코드 스캐너는 보통 엔터로 끝남)
            barcode = input().strip()
            if barcode:
                print(f"✅ 스캔된 바코드: {barcode}")
                print(f"   길이: {len(barcode)} 문자")
                print(f"   타입: {type(barcode).__name__}")
                print("-" * 50)
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        sys.exit(0)
    except EOFError:
        print("\n입력이 종료되었습니다.")
        sys.exit(0)

if __name__ == "__main__":
    try:
        read_barcode()
    except Exception as e:
        print(f"에러가 발생했습니다: {e}")
        sys.exit(1)