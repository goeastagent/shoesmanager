# 물류 관리 시스템 (Inventory Management System)

신발 관리 및 물류 추적을 위한 완전한 시스템입니다. SQLite/MySQL 데이터베이스와 연결되어 CRUD, 검색, 내보내기 기능을 지원하며, CLI와 GUI 인터페이스를 모두 제공합니다.

## 🚀 주요 기능

- **완전한 CRUD 작업**: 재고 항목의 생성, 조회, 수정, 삭제
- **강력한 검색 기능**: 키워드, 날짜 범위, 가격 범위, 다중 필드 조합 검색
- **설정 가능한 필수 항목**: config.py에서 필수 입력 항목 설정
- **기본값 자동 설정**: 위치, 구매처, 구매일 자동 설정
- **데이터 가져오기/내보내기**: CSV 형식 지원, 오류 처리 포함
- **HTML 보고서**: 시각적으로 보기 좋은 HTML 보고서 생성
- **삼중 인터페이스**: CLI (Typer), GUI (Tkinter), 웹 (FastAPI) 모두 지원
- **웹 인터페이스**: Bootstrap 기반의 반응형 웹 UI
- **바코드 스캐너 지원**: 바코드 입력 시 자동완성 및 판매 처리
- **UUID 기반 ID**: 고유한 UUID를 사용한 항목 식별
- **데이터베이스 마이그레이션**: Alembic을 통한 스키마 관리

## 📋 관리 항목 필드

| 필드명 | 타입 | 설명 | 필수 |
|--------|------|------|------|
| id | STRING(36) | 고유 식별자 (UUID) | ✅ |
| location | VARCHAR(50) | 보관 위치 | ✅ |
| purchase_date | DATE | 구매일 | ✅ |
| sale_date | DATE | 판매일 | ❌ |
| model_name | VARCHAR(100) | 모델명 | ✅ |
| name | VARCHAR(100) | 제품명 | ✅ |
| size | VARCHAR(20) | 사이즈 | ❌ |
| vendor | VARCHAR(100) | 구매처 | ✅ |
| price | DECIMAL(12,2) | 가격 | ✅ |
| notes | TEXT | 메모 | ❌ |
| created_at | DATETIME | 생성일시 | ✅ |
| updated_at | DATETIME | 수정일시 | ✅ |

## 🛠️ 기술 스택

- **Python**: >= 3.10
- **데이터베이스**: SQLite (기본) / MySQL 8.0 (선택)
- **ORM**: SQLAlchemy 2.0+
- **마이그레이션**: Alembic
- **CLI**: Typer
- **GUI**: Tkinter
- **웹**: FastAPI, Bootstrap 5, jQuery
- **검증**: Pydantic
- **설정 관리**: pydantic-settings


## 📦 설치 및 설정

### 1. 저장소 클론

```bash
git clone <repository-url>
cd 신발관리
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 설정 (선택사항)

SQLite를 사용하는 경우 별도 설정이 필요하지 않습니다. MySQL을 사용하려면 `.env` 파일을 생성하세요:

```bash
# MySQL 데이터베이스 설정
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=inventory_management
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# 애플리케이션 설정
LOG_LEVEL=INFO
DATABASE_TYPE=mysql
```

### 5. 필수 항목 설정

`app/config.py`에서 재고 등록 시 필수 입력 항목을 설정할 수 있습니다:

```python
# 필수 입력 항목 설정
required_fields: List[str] = Field(
    default=["location", "purchase_date", "model_name", "name", "vendor", "price"],
    description="재고 등록 시 필수 입력 항목"
)

# 기본값 설정
default_location: str = Field(default="A-01", description="기본 보관 위치")
default_vendor: str = Field(default="기본구매처", description="기본 구매처")
```

`.env` 파일 내용:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=inventory_management
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
LOG_LEVEL=INFO
```

### 5. 데이터베이스 초기화

SQLite를 사용하는 경우 자동으로 데이터베이스가 생성됩니다. MySQL을 사용하는 경우:

```sql
CREATE DATABASE inventory_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

그 후 데이터베이스를 초기화하세요:

```bash
python -m app.ui.cli init-db
```

## 🖥️ 사용법

### CLI 인터페이스

#### 기본 명령어

```bash
# 데이터베이스 초기화
python -m app.ui.cli init-db

# 새 항목 추가 (필수 항목: 위치, 구매일, 모델명, 제품명, 구매처, 가격)
python -m app.ui.cli add --location "A-01" --purchase-date 2024-01-01 --model-name "Nike Air Max" --name "Nike Air Max 270" --size "270" --vendor "ABC몰" --price 129000 --notes "첫 입고"

# 필수 항목만으로 간단 추가 (기본값 자동 설정)
python -m app.ui.cli add --model-name "Adidas Ultraboost" --name "Adidas Ultraboost 22" --price 159000

# 항목 목록 조회
python -m app.ui.cli list --limit 50

# 키워드 검색
python -m app.ui.cli list --keyword "Nike" --price-min 50000

# 날짜 범위 검색
python -m app.ui.cli list --purchase-date-from 2024-01-01 --purchase-date-to 2024-12-31

# 항목 상세 조회
python -m app.ui.cli show 1

# 항목 수정
python -m app.ui.cli update 1 --location "B-02" --price 99000

# 항목 삭제
python -m app.ui.cli delete 1

# CSV 가져오기
python -m app.ui.cli import-csv ./data/import.csv --has-header

# CSV 내보내기
python -m app.ui.cli export-csv ./exports/items_20240101.csv --keyword "Nike"

# HTML 내보내기
python -m app.ui.cli export-html ./reports/inventory_report.html --title "재고 보고서"

# 통계 조회
python -m app.ui.cli stats

# 통계 보고서 내보내기
python -m app.ui.cli export-stats ./reports/statistics.html
```

#### 고급 검색 예시

```bash
# 복합 조건 검색
python -m app.ui.cli list \
  --keyword "Air" \
  --location "A-01" \
  --vendor "ABC몰" \
  --price-min 100000 \
  --price-max 200000 \
  --purchase-date-from 2024-01-01 \
  --sort-by price \
  --sort-desc \
  --limit 20

# 판매된 항목만 조회
python -m app.ui.cli list --sale-date-from 2024-01-01

# 재고 항목만 조회 (판매일이 없는 항목)
python -m app.ui.cli list --sale-date-from "" --sale-date-to ""
```

### GUI 인터페이스 (Tkinter)

```bash
python -m app.ui.tk_app
```

#### GUI 주요 기능

1. **툴바**: 빠른 접근을 위한 버튼들 (새 항목, 수정, 삭제, 통계, 새로고침, 가져오기/내보내기)
2. **검색 패널**: 다양한 조건으로 실시간 검색
3. **목록 보기**: 검색 결과를 테이블 형태로 표시
4. **상세 정보**: 선택한 항목의 상세 정보 표시
5. **항목 관리**: 추가, 수정, 삭제 기능
6. **필수 항목 검증**: config.py 설정에 따른 필수 입력 항목 검증
7. **기본값 자동 설정**: 새 항목 추가 시 기본값 자동 입력
8. **데이터 가져오기/내보내기**: CSV 및 HTML 형식 지원
9. **통계 보기**: 재고 현황 및 통계 정보

### 웹 인터페이스 (FastAPI)

```bash
# 방법 1: 실행 스크립트 사용 (권장)
python run_web.py

# 방법 2: 모듈로 직접 실행
python -m app.ui.web_app

# 방법 3: 셸 스크립트 사용
./run_web.sh  # macOS/Linux
run_web.bat   # Windows
```

웹 브라우저에서 **http://localhost:8000** 으로 접속

#### 웹 UI 주요 기능

1. **반응형 디자인**: 데스크톱, 태블릿, 모바일 모두 지원
2. **바코드 스캐너 지원**: 
   - 항목 추가 시 바코드 자동완성
   - 판매 시 바코드 스캔으로 즉시 처리 (재고 1개인 경우)
3. **페이징**: 페이지당 50개 항목 표시
4. **실시간 검색**: 다양한 조건으로 필터링
5. **컬럼 정렬**: 헤더 클릭으로 오름차순/내림차순 정렬
6. **모달 다이얼로그**: 추가/수정/판매 작업
7. **상세 정보 패널**: 선택한 항목의 상세 정보 실시간 표시

> **📝 참고**: 웹 버전에서는 CSV 가져오기/내보내기, HTML 보고서, 통계 기능이 제외되었습니다. 이러한 기능이 필요한 경우 GUI 또는 CLI 인터페이스를 사용하세요.

자세한 웹 애플리케이션 사용법은 [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)를 참조하세요.

## 📊 데이터 가져오기/내보내기

### CSV 가져오기

CSV 파일 형식:
```csv
location,purchase_date,model_name,name,size,vendor,price,notes
A-01,2024-01-01,Nike Air Max,Nike Air Max 270,270,ABC몰,129000,첫 입고
A-02,2024-01-02,Adidas Ultraboost,Adidas Ultraboost 22,280,XYZ스토어,159000,인기 상품
```

지원하는 날짜 형식:
- `YYYY-MM-DD`
- `YYYY/MM/DD`
- `MM/DD/YYYY`
- `DD/MM/YYYY`

### CSV 내보내기

```bash
# 전체 데이터 내보내기
python -m app.ui.cli export-csv ./exports/all_items.csv

# 필터링된 데이터 내보내기
python -m app.ui.cli export-csv ./exports/nike_items.csv --keyword "Nike" --vendor "ABC몰"
```

### HTML 보고서

```bash
# 기본 보고서
python -m app.ui.cli export-html ./reports/inventory_report.html

# 커스텀 제목과 필터링
python -m app.ui.cli export-html ./reports/nike_report.html --title "Nike 제품 보고서" --keyword "Nike"
```



## 📁 프로젝트 구조

```
신발관리/
├── app/
│   ├── __init__.py
│   ├── config.py              # 환경 설정
│   ├── db.py                  # 데이터베이스 연결
│   ├── models.py              # SQLAlchemy 모델
│   ├── schemas.py             # Pydantic 스키마
│   ├── repository.py          # CRUD 로직
│   ├── utils.py               # 유틸리티 함수
│   ├── migrations/            # Alembic 마이그레이션
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── services/              # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── import_service.py  # CSV 가져오기
│   │   └── export_service.py  # CSV/HTML 내보내기
│   └── ui/                    # 사용자 인터페이스
│       ├── __init__.py
│       ├── cli.py             # CLI 인터페이스
│       ├── tk_app.py          # GUI 인터페이스
│       ├── web_app.py         # 웹 인터페이스
│       ├── templates/         # HTML 템플릿
│       │   └── index.html
│       └── static/            # 정적 파일
│           ├── css/
│           │   └── style.css
│           └── js/
│               └── app.js
│
├── alembic.ini               # Alembic 설정
├── requirements.txt          # 의존성 목록
├── run_web.py               # 웹 애플리케이션 실행 스크립트
├── run_web.sh               # 웹 실행 스크립트 (macOS/Linux)
├── run_web.bat              # 웹 실행 스크립트 (Windows)
├── README.md                # 프로젝트 문서
└── WEB_APP_GUIDE.md         # 웹 애플리케이션 가이드
```

## 🔧 개발 및 확장

### 새로운 필드 추가

1. `app/models.py`에서 모델 수정
2. `app/schemas.py`에서 스키마 수정
3. Alembic 마이그레이션 생성:
   ```bash
   alembic revision --autogenerate -m "Add new field"
   alembic upgrade head
   ```

### 새로운 검색 조건 추가

1. `app/schemas.py`의 `SearchQuery` 클래스에 필드 추가
2. `app/repository.py`의 `search` 메서드에 필터 로직 추가

### 새로운 내보내기 형식 추가

1. `app/services/export_service.py`에 새로운 메서드 추가
2. CLI와 GUI에 해당 명령어 추가

## 🐛 문제 해결

### 일반적인 문제

1. **데이터베이스 연결 실패**
   - MySQL 서비스가 실행 중인지 확인
   - `.env` 파일의 데이터베이스 설정 확인
   - 사용자 권한 확인

2. **CSV 가져오기 실패**
   - 파일 인코딩 확인 (UTF-8 권장)
   - 필수 컬럼 존재 여부 확인
   - 날짜 형식 확인

3. **GUI 실행 실패**
   - Tkinter 설치 확인: `python -c "import tkinter"`
   - 디스플레이 설정 확인 (Linux)

### 로그 확인

```bash
# 로그 레벨을 DEBUG로 설정하여 상세 로그 확인
export LOG_LEVEL=DEBUG
python -m app.ui.cli list
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.

---

**물류 관리 시스템**으로 효율적인 재고 관리를 시작하세요! 🚀
