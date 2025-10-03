# Python 기반 빌드 시스템

## 🐍 Python 스크립트 사용의 장점

- ✅ **크로스 플랫폼**: Windows, macOS, Linux 모두 지원
- ✅ **안정성**: 배치 파일보다 에러 처리 우수
- ✅ **유연성**: 복잡한 로직 구현 가능
- ✅ **디버깅**: 에러 메시지와 로그가 명확
- ✅ **유지보수**: 코드 관리가 쉬움

## 🚀 빠른 시작

### 새로운 환경에서

```bash
# 1. 프로젝트 다운로드/복사
# 2. Python 설치 (3.8 이상)
# 3. 통합 빌드 도구 실행
python build.py
```

### 기존 환경에서

```bash
# GUI만 실행
python run.py

# 또는 직접 실행
python -m app.ui.tk_app
```

## 📋 사용 가능한 명령어

### `python build.py` - 통합 빌드 도구

인터랙티브 메뉴가 표시됩니다:

```
1. 🚀 Complete Setup (Environment + Database + Build)
2. 🔧 Setup Environment Only  
3. 🗄️ Initialize Database Only
4. 🔨 Build Executable Only
5. ▶️ Run GUI Application
6. 📋 Show Status
7. ❌ Exit
```

### 명령줄 옵션

```bash
python build.py complete    # 전체 설정
python build.py setup       # 환경 설정만
python build.py database    # DB 초기화만
python build.py build       # 빌드만
python build.py run         # GUI 실행
python build.py status      # 상태 확인
```

### `python run.py` - 빠른 실행

가상환경이 설정되어 있다면 GUI를 바로 실행합니다.

## 🔧 빌드 과정

### 1. 환경 검증
- Python 버전 확인 (3.8+)
- 프로젝트 구조 검증
- 필요한 파일 존재 확인

### 2. 가상환경 설정
- `venv` 폴더 생성
- pip 업그레이드
- 의존성 설치

### 3. 데이터베이스 초기화
- 새 DB 파일 생성
- 테이블 생성
- 샘플 데이터 추가

### 4. 실행파일 빌드
- PyInstaller 설치
- Spec 파일 생성
- 실행파일 빌드
- 배포 패키지 생성

## 📁 생성되는 파일들

```
dist/
├── ShoesManager.exe          # 실행파일
├── USER_GUIDE.txt           # 사용자 가이드
└── inventory_management.db   # 초기화된 DB

venv/                        # 가상환경
├── Scripts/ (Windows)
└── bin/ (macOS/Linux)
```

## 🛠️ 문제 해결

### Python이 설치되지 않은 경우

1. **Windows**: https://www.python.org/downloads/
2. **macOS**: `brew install python3`
3. **Linux**: `sudo apt install python3 python3-pip`

### 가상환경 문제

```bash
# 가상환경 재생성
rm -rf venv
python build.py setup
```

### 의존성 문제

```bash
# 의존성 재설치
python build.py setup
```

### 빌드 실패

```bash
# 상태 확인
python build.py status

# 단계별 실행
python build.py database
python build.py build
```

## 🎯 권장 워크플로우

### 개발자용

```bash
# 1. 프로젝트 클론
git clone <repository>
cd shoesmanager

# 2. 환경 설정
python build.py complete

# 3. 개발 중 GUI 실행
python run.py
```

### 사용자용

```bash
# 1. 프로젝트 다운로드
# 2. Python 설치
# 3. 빌드 실행
python build.py complete

# 4. 실행파일 사용
dist/ShoesManager.exe
```

## 🔄 업데이트

새로운 기능이 추가되면:

```bash
# 1. 코드 업데이트
git pull

# 2. 의존성 업데이트
python build.py setup

# 3. 새 빌드
python build.py build
```

## 📞 지원

문제가 발생하면:

1. **상태 확인**: `python build.py status`
2. **로그 확인**: 에러 메시지 자세히 읽기
3. **단계별 실행**: 각 단계를 개별적으로 실행
4. **개발자 문의**: 문제 상황과 에러 메시지 전달

## ✅ 체크리스트

- [ ] Python 3.8+ 설치됨
- [ ] 프로젝트 파일 다운로드됨
- [ ] `python build.py` 실행 성공
- [ ] 가상환경 생성됨
- [ ] 의존성 설치됨
- [ ] DB 초기화됨
- [ ] 실행파일 생성됨
- [ ] GUI 실행 테스트 완료

모든 항목이 체크되면 신발 관리 시스템을 사용할 준비가 완료됩니다!
