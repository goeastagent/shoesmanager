# 윈도우 실행파일 빌드 가이드

## 📋 개요
이 가이드는 신발 관리 시스템을 윈도우 실행파일(.exe)로 빌드하는 방법을 설명합니다.

## 🛠️ 필요한 도구
- Python 3.8 이상
- PyInstaller
- 가상환경 (venv)

## 🚀 빌드 방법

### 방법 1: 배치 파일 사용 (권장)
```bash
# 윈도우에서 배치 파일 실행
build.bat
```

### 방법 2: Python 스크립트 직접 실행
```bash
# 가상환경 활성화
venv\Scripts\activate.bat

# 빌드 스크립트 실행
python build_windows.py
```

### 방법 3: 수동 빌드
```bash
# 1. 가상환경 활성화
venv\Scripts\activate.bat

# 2. PyInstaller 설치
pip install pyinstaller

# 3. 빌드 실행
pyinstaller --clean --noconfirm ShoesManager.spec
```

## 📁 빌드 결과
빌드가 완료되면 다음 파일들이 생성됩니다:

```
dist/
├── ShoesManager.exe          # 실행파일
├── README.txt               # 사용자 가이드
└── ShoesManager/            # 추가 파일들 (필요시)
```

## ⚙️ 빌드 설정

### spec 파일 주요 설정
- `console=False`: GUI 애플리케이션이므로 콘솔 창 숨김
- `upx=True`: 실행파일 압축으로 크기 최적화
- `datas`: 필요한 데이터 파일들 포함

### 포함되는 파일들
- 모든 Python 모듈
- 데이터베이스 파일 (inventory_management.db)
- 설정 파일들
- 마이그레이션 파일들

## 🔧 문제 해결

### 일반적인 문제들

1. **빌드 실패**
   ```bash
   # 의존성 재설치
   pip install -r requirements.txt
   ```

2. **실행파일이 실행되지 않음**
   - 관리자 권한으로 실행
   - 바이러스 백신 예외 처리
   - Windows Defender 예외 추가

3. **데이터베이스 오류**
   - inventory_management.db 파일이 포함되었는지 확인
   - 실행파일과 같은 폴더에 DB 파일이 있는지 확인

4. **모듈을 찾을 수 없음**
   - spec 파일의 `hiddenimports`에 누락된 모듈 추가
   - `datas` 섹션에 필요한 파일 추가

## 📦 배포

### 단일 실행파일 배포
```bash
# UPX를 사용한 압축 빌드
pyinstaller --onefile --windowed --upx-dir=upx ShoesManager.spec
```

### 폴더 형태 배포
```bash
# 폴더 형태로 빌드 (기본값)
pyinstaller --windowed ShoesManager.spec
```

## 🎯 최적화 팁

1. **실행파일 크기 줄이기**
   - 불필요한 모듈 제외
   - UPX 압축 사용
   - 가상환경에서 빌드

2. **실행 속도 향상**
   - `--optimize=2` 옵션 사용
   - 불필요한 디버그 정보 제거

3. **안정성 향상**
   - 테스트 환경에서 충분히 테스트
   - 다양한 윈도우 버전에서 테스트

## 📞 지원

빌드 과정에서 문제가 발생하면:
1. 에러 메시지를 확인하세요
2. 로그 파일을 확인하세요
3. 개발자에게 문의하세요

## 🔄 업데이트

새로운 기능이 추가되면:
1. 코드 변경사항 커밋
2. 빌드 스크립트 재실행
3. 새로운 실행파일 배포
