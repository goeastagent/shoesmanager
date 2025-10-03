# Python 설치 가이드

## 🐍 Python 설치가 필요한 경우

`setup_new_environment.bat` 실행 시 "ERROR: Python is not installed or not in PATH" 에러가 발생하는 경우, Python이 설치되어 있지 않거나 PATH에 등록되지 않은 상태입니다.

## 📥 Python 설치 방법

### 방법 1: 공식 웹사이트에서 다운로드 (권장)

1. **Python 공식 웹사이트 방문**
   - https://www.python.org/downloads/
   - "Download Python" 버튼 클릭

2. **설치 파일 다운로드**
   - Windows용 설치 파일이 자동으로 다운로드됩니다
   - 파일명: `python-3.x.x-amd64.exe` (버전에 따라 다름)

3. **설치 실행**
   - 다운로드한 파일을 더블클릭하여 실행
   - **중요**: "Add Python to PATH" 체크박스를 반드시 선택하세요!
   - "Install for all users"도 선택하는 것을 권장합니다

4. **설치 완료 후**
   - 명령 프롬프트를 다시 시작하세요
   - `python --version` 명령어로 설치 확인

### 방법 2: Microsoft Store에서 설치

1. **Microsoft Store 열기**
2. **"Python" 검색**
3. **Python 3.x 설치** (최신 버전 선택)
4. **설치 완료 후 명령 프롬프트 재시작**

### 방법 3: Anaconda 설치

1. **Anaconda 웹사이트 방문**
   - https://www.anaconda.com/products/distribution
2. **Windows용 Anaconda 다운로드**
3. **설치 실행** (PATH 자동 설정됨)

## 🔍 Python 설치 확인

설치 완료 후 다음 명령어들로 확인할 수 있습니다:

```cmd
python --version
py --version
python3 --version
py -3 --version
```

하나라도 버전이 표시되면 설치가 성공한 것입니다.

## ⚠️ 일반적인 문제와 해결책

### 문제 1: "python은 내부 또는 외부 명령이 아닙니다"

**원인**: Python이 PATH에 등록되지 않음

**해결책**:
1. Python 재설치 시 "Add Python to PATH" 체크
2. 수동으로 PATH 추가:
   - 시스템 속성 → 고급 → 환경 변수
   - PATH에 Python 설치 경로 추가

### 문제 2: 여러 Python 버전이 설치됨

**해결책**:
- `py` 명령어 사용 (Python Launcher)
- 또는 `py -3` 명령어 사용

### 문제 3: 권한 문제

**해결책**:
- 관리자 권한으로 명령 프롬프트 실행
- "Install for all users" 옵션으로 재설치

## 🚀 설치 후 다음 단계

Python 설치가 완료되면:

1. **명령 프롬프트 재시작**
2. **프로젝트 폴더로 이동**
3. **설정 스크립트 실행**:
   ```cmd
   setup_new_environment_advanced.bat
   ```

## 📞 추가 도움

Python 설치에 문제가 있다면:

1. **Python 공식 문서**: https://docs.python.org/3/using/windows.html
2. **Python 커뮤니티**: https://www.python.org/community/
3. **개발자 문의**: 프로젝트 개발자에게 문의

## ✅ 설치 확인 체크리스트

- [ ] Python 다운로드 완료
- [ ] 설치 시 "Add Python to PATH" 체크
- [ ] 설치 완료 후 명령 프롬프트 재시작
- [ ] `python --version` 명령어로 버전 확인
- [ ] 프로젝트 폴더에서 설정 스크립트 실행
- [ ] 가상환경 생성 성공
- [ ] 의존성 설치 성공
- [ ] 데이터베이스 초기화 성공

모든 항목이 체크되면 신발 관리 시스템을 사용할 준비가 완료됩니다!
