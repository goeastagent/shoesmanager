"""
Typer 기반 CLI 인터페이스

물류 관리 시스템의 명령줄 인터페이스를 제공합니다.
"""

import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

import typer
from tabulate import tabulate

from app.config import setup_logging, settings
from app.db import db_manager, check_database_connection
from app.models import Base
from app.repository import InventoryRepository
from app.schemas import (
    InventoryItemCreate, InventoryItemUpdate, SearchQuery
)
from app.services.import_service import CSVImportService
from app.services.export_service import ExportService

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)

# Typer 앱 생성
app = typer.Typer(
    name="inventory-cli",
    help="물류 관리 시스템 CLI",
    add_completion=False
)


def get_repository() -> InventoryRepository:
    """Repository 인스턴스 생성"""
    session = db_manager.get_session()
    return InventoryRepository(session)


def parse_date_string(date_str: Optional[str]):
    """날짜 문자열을 date 객체로 파싱"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise typer.BadParameter(f"날짜 형식이 올바르지 않습니다: {date_str}. YYYY-MM-DD 형식을 사용하세요.")


def parse_decimal_string(decimal_str: Optional[str]) -> Optional[Decimal]:
    """Decimal 문자열을 Decimal 객체로 파싱"""
    if not decimal_str:
        return None
    try:
        return Decimal(decimal_str)
    except (ValueError, TypeError):
        raise typer.BadParameter(f"가격 형식이 올바르지 않습니다: {decimal_str}")


@app.command()
def init_db():
    """데이터베이스 초기화"""
    try:
        typer.echo("데이터베이스 연결 확인 중...")
        
        if not check_database_connection():
            typer.echo("❌ 데이터베이스 연결에 실패했습니다.", err=True)
            raise typer.Exit(1)
        
        typer.echo("✅ 데이터베이스 연결 성공")
        
        # 테이블 생성
        typer.echo("테이블 생성 중...")
        Base.metadata.create_all(bind=db_manager.engine)
        
        typer.echo("✅ 데이터베이스 초기화 완료")
        
    except Exception as e:
        typer.echo(f"❌ 데이터베이스 초기화 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def add(
    location: Optional[str] = typer.Option(None, "--location", "-l", help="보관 위치"),
    purchase_date: Optional[str] = typer.Option(None, "--purchase-date", "-p", help="구매일 (YYYY-MM-DD)"),
    model_name: Optional[str] = typer.Option(None, "--model-name", "-m", help="모델명"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="제품명"),
    vendor: Optional[str] = typer.Option(None, "--vendor", "-v", help="구매처"),
    price: Optional[str] = typer.Option(None, "--price", help="가격"),
    size: Optional[str] = typer.Option(None, "--size", "-s", help="사이즈"),
    barcode: Optional[str] = typer.Option(None, "--barcode", "-b", help="바코드"),
    sale_date: Optional[str] = typer.Option(None, "--sale-date", help="판매일 (YYYY-MM-DD)"),
    notes: Optional[str] = typer.Option(None, "--notes", help="메모")
):
    """새로운 재고 항목 추가"""
    try:
        # 필수 항목 검증
        required_data = {
            "location": location,
            "purchase_date": purchase_date,
            "model_name": model_name,
            "name": name,
            "vendor": vendor,
            "price": price
        }
        
        missing_fields = []
        for field in settings.required_fields:
            if not required_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            field_labels = {
                "location": "위치",
                "purchase_date": "구매일",
                "model_name": "모델명", 
                "name": "제품명",
                "vendor": "구매처",
                "price": "가격"
            }
            missing_labels = [field_labels.get(f, f) for f in missing_fields]
            typer.echo(f"❌ 필수 항목이 누락되었습니다: {', '.join(missing_labels)}", err=True)
            raise typer.Exit(1)
        
        # 기본값 설정
        if not location:
            location = settings.default_location
        if not vendor:
            vendor = settings.default_vendor
        if not purchase_date:
            from datetime import datetime
            purchase_date = datetime.now().strftime('%Y-%m-%d')
        
        # 날짜 파싱
        parsed_purchase_date = parse_date_string(purchase_date)
        parsed_sale_date = parse_date_string(sale_date)
        
        # 가격 파싱
        parsed_price = parse_decimal_string(price)
        
        item_data = InventoryItemCreate(
            location=location,
            purchase_date=parsed_purchase_date,
            sale_date=parsed_sale_date,
            model_name=model_name,
            name=name,
            size=size,
            barcode=barcode,
            vendor=vendor,
            price=parsed_price,
            notes=notes
        )
        
        # 세션 컨텍스트 매니저 사용
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            created_item = repository.create_with_barcode_update(item_data)
            
            typer.echo("✅ 재고 항목이 성공적으로 추가되었습니다.")
            typer.echo(f"ID: {created_item.id}")
            typer.echo(f"이름: {created_item.name}")
            typer.echo(f"모델: {created_item.model_name}")
            typer.echo(f"위치: {created_item.location}")
            typer.echo(f"가격: ₩{created_item.price:,.0f}")
        
    except Exception as e:
        typer.echo(f"❌ 항목 추가 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def get_barcode(
    barcode: str = typer.Argument(..., help="조회할 바코드")
):
    """바코드 정보 조회"""
    try:
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            barcode_info = repository.get_barcode_info(barcode)
            
            if not barcode_info:
                typer.echo(f"❌ 바코드 '{barcode}'를 찾을 수 없습니다.", err=True)
                raise typer.Exit(1)
            
            typer.echo("✅ 바코드 정보 조회 완료")
            typer.echo(f"바코드: {barcode_info.barcode}")
            typer.echo(f"모델명: {barcode_info.model_name}")
            typer.echo(f"제품명: {barcode_info.name}")
            typer.echo(f"생성일: {barcode_info.created_at}")
            typer.echo(f"수정일: {barcode_info.updated_at}")
            
    except Exception as e:
        typer.echo(f"❌ 바코드 조회 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def list(
    keyword: Optional[str] = typer.Option(None, "--keyword", "-k", help="검색 키워드"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="위치"),
    model_name: Optional[str] = typer.Option(None, "--model-name", "-m", help="모델명"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="제품명"),
    vendor: Optional[str] = typer.Option(None, "--vendor", "-v", help="구매처"),
    size: Optional[str] = typer.Option(None, "--size", "-s", help="사이즈"),
    barcode: Optional[str] = typer.Option(None, "--barcode", "-b", help="바코드"),
    purchase_date_from: Optional[str] = typer.Option(None, "--purchase-date-from", help="구매일 시작"),
    purchase_date_to: Optional[str] = typer.Option(None, "--purchase-date-to", help="구매일 종료"),
    sale_date_from: Optional[str] = typer.Option(None, "--sale-date-from", help="판매일 시작"),
    sale_date_to: Optional[str] = typer.Option(None, "--sale-date-to", help="판매일 종료"),
    price_min: Optional[str] = typer.Option(None, "--price-min", help="최소 가격"),
    price_max: Optional[str] = typer.Option(None, "--price-max", help="최대 가격"),
    sort_by: str = typer.Option("created_at", "--sort-by", help="정렬 기준 (purchase_date, sale_date, price, created_at)"),
    sort_desc: bool = typer.Option(True, "--sort-desc/--sort-asc", help="내림차순 정렬"),
    limit: int = typer.Option(50, "--limit", help="결과 제한"),
    offset: int = typer.Option(0, "--offset", help="결과 오프셋")
):
    """재고 항목 목록 조회"""
    try:
        search_query = SearchQuery(
            keyword=keyword,
            location=location,
            model_name=model_name,
            name=name,
            vendor=vendor,
            size=size,
            barcode=barcode,
            purchase_date_from=parse_date_string(purchase_date_from),
            purchase_date_to=parse_date_string(purchase_date_to),
            sale_date_from=parse_date_string(sale_date_from),
            sale_date_to=parse_date_string(sale_date_to),
            price_min=parse_decimal_string(price_min),
            price_max=parse_decimal_string(price_max),
            sort_by=sort_by,
            sort_desc=sort_desc,
            limit=limit,
            offset=offset
        )
        
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            result = repository.search(search_query)
        
        if not result.items:
            typer.echo("검색 결과가 없습니다.")
            return
        
        # 테이블 헤더
        headers = [
            "ID", "위치", "구매일", "판매일", "모델명", "이름",
            "사이즈", "바코드", "구매처", "가격", "상태"
        ]
        
        # 테이블 데이터
        table_data = []
        for item in result.items:
            status = "판매됨" if item.sale_date else "재고"
            table_data.append([
                item.id,
                item.location,
                item.purchase_date.strftime('%Y-%m-%d') if item.purchase_date else '',
                item.sale_date.strftime('%Y-%m-%d') if item.sale_date else '',
                item.model_name,
                item.name,
                item.size or '',
                item.barcode or '',
                item.vendor,
                f"₩{item.price:,.0f}",
                status
            ])
        
        # 테이블 출력
        typer.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
        typer.echo(f"\n총 {result.total_count}개 항목 중 {len(result.items)}개 표시")
        
        if result.has_more:
            typer.echo(f"더 많은 결과가 있습니다. --offset {offset + limit} --limit {limit}로 조회하세요.")
        
    except Exception as e:
        typer.echo(f"❌ 목록 조회 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def show(
    item_id: int = typer.Argument(..., help="항목 ID")
):
    """재고 항목 상세 조회"""
    try:
        repository = get_repository()
        
        item = repository.get_by_id(item_id)
        if not item:
            typer.echo(f"❌ ID {item_id}인 항목을 찾을 수 없습니다.", err=True)
            raise typer.Exit(1)
        
        # 상세 정보 출력
        typer.echo("=" * 50)
        typer.echo(f"재고 항목 상세 정보 (ID: {item.id})")
        typer.echo("=" * 50)
        typer.echo(f"위치: {item.location}")
        typer.echo(f"구매일: {item.purchase_date}")
        typer.echo(f"판매일: {item.sale_date or '미판매'}")
        typer.echo(f"모델명: {item.model_name}")
        typer.echo(f"이름: {item.name}")
        typer.echo(f"사이즈: {item.size or '미지정'}")
        typer.echo(f"구매처: {item.vendor}")
        typer.echo(f"가격: ₩{item.price:,.0f}")
        typer.echo(f"상태: {'판매됨' if item.sale_date else '재고'}")
        typer.echo(f"메모: {item.notes or '없음'}")
        typer.echo(f"생성일시: {item.created_at}")
        typer.echo(f"수정일시: {item.updated_at}")
        
    except Exception as e:
        typer.echo(f"❌ 상세 조회 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def update(
    item_id: int = typer.Argument(..., help="항목 ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="보관 위치"),
    purchase_date: Optional[str] = typer.Option(None, "--purchase-date", "-p", help="구매일 (YYYY-MM-DD)"),
    model_name: Optional[str] = typer.Option(None, "--model-name", "-m", help="모델명"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="제품명"),
    vendor: Optional[str] = typer.Option(None, "--vendor", "-v", help="구매처"),
    price: Optional[str] = typer.Option(None, "--price", help="가격"),
    size: Optional[str] = typer.Option(None, "--size", "-s", help="사이즈"),
    sale_date: Optional[str] = typer.Option(None, "--sale-date", help="판매일 (YYYY-MM-DD)"),
    notes: Optional[str] = typer.Option(None, "--notes", help="메모")
):
    """재고 항목 수정"""
    try:
        repository = get_repository()
        
        # 수정할 데이터 준비
        update_data = InventoryItemUpdate(
            location=location,
            purchase_date=parse_date_string(purchase_date),
            sale_date=parse_date_string(sale_date),
            model_name=model_name,
            name=name,
            size=size,
            vendor=vendor,
            price=parse_decimal_string(price),
            notes=notes
        )
        
        updated_item = repository.update(item_id, update_data)
        if not updated_item:
            typer.echo(f"❌ ID {item_id}인 항목을 찾을 수 없습니다.", err=True)
            raise typer.Exit(1)
        
        typer.echo("✅ 재고 항목이 성공적으로 수정되었습니다.")
        typer.echo(f"ID: {updated_item.id}")
        typer.echo(f"이름: {updated_item.name}")
        typer.echo(f"모델: {updated_item.model_name}")
        typer.echo(f"위치: {updated_item.location}")
        typer.echo(f"가격: ₩{updated_item.price:,.0f}")
        
    except Exception as e:
        typer.echo(f"❌ 항목 수정 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def delete(
    item_id: int = typer.Argument(..., help="항목 ID"),
    force: bool = typer.Option(False, "--force", "-f", help="확인 없이 삭제")
):
    """재고 항목 삭제"""
    try:
        repository = get_repository()
        
        # 항목 존재 확인
        item = repository.get_by_id(item_id)
        if not item:
            typer.echo(f"❌ ID {item_id}인 항목을 찾을 수 없습니다.", err=True)
            raise typer.Exit(1)
        
        # 확인 메시지
        if not force:
            typer.echo(f"삭제할 항목: {item.name} (ID: {item.id})")
            if not typer.confirm("정말로 삭제하시겠습니까?"):
                typer.echo("삭제가 취소되었습니다.")
                return
        
        # 삭제 실행
        success = repository.delete(item_id)
        if success:
            typer.echo("✅ 재고 항목이 성공적으로 삭제되었습니다.")
        else:
            typer.echo("❌ 항목 삭제에 실패했습니다.", err=True)
            raise typer.Exit(1)
        
    except Exception as e:
        typer.echo(f"❌ 항목 삭제 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def import_csv(
    file_path: str = typer.Argument(..., help="CSV 파일 경로"),
    has_header: bool = typer.Option(True, "--has-header/--no-header", help="헤더 포함 여부"),
    encoding: str = typer.Option("utf-8", "--encoding", help="파일 인코딩")
):
    """CSV 파일에서 데이터 가져오기"""
    try:
        repository = get_repository()
        import_service = CSVImportService(repository)
        
        typer.echo(f"CSV 파일 가져오기 시작: {file_path}")
        
        result = import_service.import_from_csv(file_path, has_header, encoding)
        
        typer.echo("=" * 50)
        typer.echo("가져오기 결과")
        typer.echo("=" * 50)
        typer.echo(f"성공: {result.success_count}개")
        typer.echo(f"실패: {result.error_count}개")
        
        if result.error_count > 0:
            typer.echo(f"오류 파일: {result.error_file_path}")
            typer.echo("오류 상세:")
            for error in result.errors[:5]:  # 처음 5개 오류만 표시
                typer.echo(f"  행 {error['row']}: {error['error']}")
            
            if len(result.errors) > 5:
                typer.echo(f"  ... 및 {len(result.errors) - 5}개 추가 오류")
        
        if result.success_count > 0:
            typer.echo("✅ 가져오기가 완료되었습니다.")
        else:
            typer.echo("❌ 가져오기에 실패했습니다.", err=True)
            raise typer.Exit(1)
        
    except Exception as e:
        typer.echo(f"❌ CSV 가져오기 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def export_csv(
    file_path: str = typer.Argument(..., help="출력 CSV 파일 경로"),
    keyword: Optional[str] = typer.Option(None, "--keyword", "-k", help="검색 키워드"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="위치"),
    model_name: Optional[str] = typer.Option(None, "--model-name", "-m", help="모델명"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="제품명"),
    vendor: Optional[str] = typer.Option(None, "--vendor", "-v", help="구매처"),
    size: Optional[str] = typer.Option(None, "--size", "-s", help="사이즈"),
    purchase_date_from: Optional[str] = typer.Option(None, "--purchase-date-from", help="구매일 시작"),
    purchase_date_to: Optional[str] = typer.Option(None, "--purchase-date-to", help="구매일 종료"),
    sale_date_from: Optional[str] = typer.Option(None, "--sale-date-from", help="판매일 시작"),
    sale_date_to: Optional[str] = typer.Option(None, "--sale-date-to", help="판매일 종료"),
    price_min: Optional[str] = typer.Option(None, "--price-min", help="최소 가격"),
    price_max: Optional[str] = typer.Option(None, "--price-max", help="최대 가격"),
    include_headers: bool = typer.Option(True, "--include-headers/--no-headers", help="헤더 포함 여부")
):
    """CSV 형식으로 데이터 내보내기"""
    try:
        repository = get_repository()
        export_service = ExportService(repository)
        
        # 검색 조건 설정
        search_query = None
        if any([keyword, location, model_name, name, vendor, size, 
                purchase_date_from, purchase_date_to, sale_date_from, sale_date_to,
                price_min, price_max]):
            search_query = SearchQuery(
                keyword=keyword,
                location=location,
                model_name=model_name,
                name=name,
                vendor=vendor,
                size=size,
                purchase_date_from=parse_date_string(purchase_date_from),
                purchase_date_to=parse_date_string(purchase_date_to),
                sale_date_from=parse_date_string(sale_date_from),
                sale_date_to=parse_date_string(sale_date_to),
                price_min=parse_decimal_string(price_min),
                price_max=parse_decimal_string(price_max),
                limit=10000  # 큰 제한으로 전체 데이터 내보내기
            )
        
        typer.echo(f"CSV 내보내기 시작: {file_path}")
        
        output_path = export_service.export_to_csv(file_path, search_query, include_headers)
        
        typer.echo(f"✅ CSV 내보내기 완료: {output_path}")
        
    except Exception as e:
        typer.echo(f"❌ CSV 내보내기 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def export_html(
    file_path: str = typer.Argument(..., help="출력 HTML 파일 경로"),
    title: str = typer.Option("재고 관리 보고서", "--title", help="보고서 제목"),
    keyword: Optional[str] = typer.Option(None, "--keyword", "-k", help="검색 키워드"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="위치"),
    model_name: Optional[str] = typer.Option(None, "--model-name", "-m", help="모델명"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="제품명"),
    vendor: Optional[str] = typer.Option(None, "--vendor", "-v", help="구매처"),
    size: Optional[str] = typer.Option(None, "--size", "-s", help="사이즈"),
    purchase_date_from: Optional[str] = typer.Option(None, "--purchase-date-from", help="구매일 시작"),
    purchase_date_to: Optional[str] = typer.Option(None, "--purchase-date-to", help="구매일 종료"),
    sale_date_from: Optional[str] = typer.Option(None, "--sale-date-from", help="판매일 시작"),
    sale_date_to: Optional[str] = typer.Option(None, "--sale-date-to", help="판매일 종료"),
    price_min: Optional[str] = typer.Option(None, "--price-min", help="최소 가격"),
    price_max: Optional[str] = typer.Option(None, "--price-max", help="최대 가격")
):
    """HTML 형식으로 데이터 내보내기"""
    try:
        repository = get_repository()
        export_service = ExportService(repository)
        
        # 검색 조건 설정
        search_query = None
        if any([keyword, location, model_name, name, vendor, size, 
                purchase_date_from, purchase_date_to, sale_date_from, sale_date_to,
                price_min, price_max]):
            search_query = SearchQuery(
                keyword=keyword,
                location=location,
                model_name=model_name,
                name=name,
                vendor=vendor,
                size=size,
                purchase_date_from=purchase_date_from,
                purchase_date_to=purchase_date_to,
                sale_date_from=sale_date_from,
                sale_date_to=sale_date_to,
                price_min=price_min,
                price_max=price_max,
                limit=10000
            )
        
        typer.echo(f"HTML 내보내기 시작: {file_path}")
        
        output_path = export_service.export_to_html(file_path, search_query, title)
        
        typer.echo(f"✅ HTML 내보내기 완료: {output_path}")
        
    except Exception as e:
        typer.echo(f"❌ HTML 내보내기 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def stats():
    """재고 통계 조회"""
    try:
        repository = get_repository()
        
        stats_data = repository.get_statistics()
        vendors = repository.get_vendors()
        locations = repository.get_locations()
        
        typer.echo("=" * 50)
        typer.echo("재고 통계")
        typer.echo("=" * 50)
        typer.echo(f"전체 항목: {stats_data['total_items']:,}개")
        typer.echo(f"재고 항목: {stats_data['in_stock_items']:,}개")
        typer.echo(f"판매된 항목: {stats_data['sold_items']:,}개")
        typer.echo(f"총 재고 가치: ₩{stats_data['total_value']:,.0f}")
        typer.echo(f"평균 가격: ₩{stats_data['average_price']:,.0f}")
        typer.echo(f"최고 가격: ₩{stats_data['max_price']:,.0f}")
        typer.echo(f"최저 가격: ₩{stats_data['min_price']:,.0f}")
        
        typer.echo("\n" + "=" * 50)
        typer.echo("구매처 목록")
        typer.echo("=" * 50)
        for vendor in vendors:
            typer.echo(f"• {vendor}")
        
        typer.echo("\n" + "=" * 50)
        typer.echo("위치 목록")
        typer.echo("=" * 50)
        for location in locations:
            typer.echo(f"• {location}")
        
    except Exception as e:
        typer.echo(f"❌ 통계 조회 실패: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def export_stats(
    file_path: str = typer.Argument(..., help="출력 HTML 파일 경로")
):
    """통계 보고서 내보내기"""
    try:
        repository = get_repository()
        export_service = ExportService(repository)
        
        typer.echo(f"통계 보고서 내보내기 시작: {file_path}")
        
        output_path = export_service.export_statistics_report(file_path)
        
        typer.echo(f"✅ 통계 보고서 내보내기 완료: {output_path}")
        
    except Exception as e:
        typer.echo(f"❌ 통계 보고서 내보내기 실패: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
