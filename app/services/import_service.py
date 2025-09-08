"""
CSV 가져오기 서비스

CSV 파일에서 데이터를 읽어와 유효성 검증 후 데이터베이스에 저장합니다.
"""

import csv
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.schemas import InventoryItemCreate, ImportResult
from app.repository import InventoryRepository

logger = logging.getLogger(__name__)


class CSVImportService:
    """CSV 가져오기 서비스 클래스"""
    
    # CSV 컬럼 매핑
    COLUMN_MAPPING = {
        'location': ['location', '위치', '보관위치'],
        'purchase_date': ['purchase_date', 'purchase date', '구매일', '구매날짜'],
        'sale_date': ['sale_date', 'sale date', '판매일', '판매날짜'],
        'model_name': ['model_name', 'model name', 'model', '모델명', '모델'],
        'name': ['name', 'product_name', 'product name', '제품명', '이름', '상품명'],
        'size': ['size', '사이즈', '크기'],
        'vendor': ['vendor', '구매처', '공급업체', 'supplier'],
        'price': ['price', '가격', '단가'],
        'notes': ['notes', 'memo', '메모', '비고', '설명']
    }
    
    def __init__(self, repository: InventoryRepository):
        """
        CSV 가져오기 서비스 초기화
        
        Args:
            repository: 재고 Repository 인스턴스
        """
        self.repository = repository
    
    def import_from_csv(
        self, 
        file_path: str, 
        has_header: bool = True,
        encoding: str = 'utf-8'
    ) -> ImportResult:
        """
        CSV 파일에서 데이터 가져오기
        
        Args:
            file_path: CSV 파일 경로
            has_header: 헤더 포함 여부
            encoding: 파일 인코딩
            
        Returns:
            ImportResult: 가져오기 결과
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
            
            # CSV 파일 읽기
            rows, headers = self._read_csv_file(file_path, has_header, encoding)
            
            # 컬럼 매핑
            column_mapping = self._map_columns(headers) if has_header else None
            
            # 데이터 파싱 및 검증
            valid_items = []
            errors = []
            
            for row_index, row in enumerate(rows, start=2 if has_header else 1):  # 헤더가 있으면 2부터 시작
                try:
                    item_data = self._parse_row(row, column_mapping, row_index)
                    valid_items.append(item_data)
                except Exception as e:
                    errors.append({
                        'row': row_index,
                        'data': row,
                        'error': str(e)
                    })
            
            # 유효한 데이터 저장
            success_count = 0
            if valid_items:
                try:
                    created_items = self.repository.bulk_create(valid_items)
                    success_count = len(created_items)
                except Exception as e:
                    logger.error(f"데이터베이스 저장 실패: {e}")
                    # 저장 실패 시 모든 항목을 오류로 처리
                    for item in valid_items:
                        errors.append({
                            'row': 'N/A',
                            'data': item.dict(),
                            'error': f"데이터베이스 저장 실패: {e}"
                        })
                    success_count = 0
            
            # 오류 파일 생성
            error_file_path = None
            if errors:
                error_file_path = self._create_error_file(file_path, errors)
            
            result = ImportResult(
                success_count=success_count,
                error_count=len(errors),
                errors=errors,
                error_file_path=error_file_path
            )
            
            logger.info(f"CSV 가져오기 완료: 성공 {success_count}개, 실패 {len(errors)}개")
            return result
            
        except Exception as e:
            logger.error(f"CSV 가져오기 실패: {e}")
            raise
    
    def _read_csv_file(
        self, 
        file_path: Path, 
        has_header: bool, 
        encoding: str
    ) -> Tuple[List[List[str]], List[str]]:
        """
        CSV 파일 읽기
        
        Args:
            file_path: CSV 파일 경로
            has_header: 헤더 포함 여부
            encoding: 파일 인코딩
            
        Returns:
            Tuple[List[List[str]], List[str]]: (데이터 행들, 헤더)
        """
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
            
            if not rows:
                raise ValueError("CSV 파일이 비어있습니다.")
            
            headers = rows[0] if has_header else None
            data_rows = rows[1:] if has_header else rows
            
            return data_rows, headers
            
        except UnicodeDecodeError:
            # UTF-8 실패 시 다른 인코딩 시도
            encodings = ['cp949', 'euc-kr', 'latin-1']
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc, newline='') as file:
                        reader = csv.reader(file)
                        rows = list(reader)
                    
                    if not rows:
                        raise ValueError("CSV 파일이 비어있습니다.")
                    
                    headers = rows[0] if has_header else None
                    data_rows = rows[1:] if has_header else rows
                    
                    logger.info(f"파일 인코딩 {enc}로 성공적으로 읽음")
                    return data_rows, headers
                    
                except UnicodeDecodeError:
                    continue
            
            raise ValueError("파일 인코딩을 확인할 수 없습니다. UTF-8, CP949, EUC-KR을 시도했습니다.")
    
    def _map_columns(self, headers: List[str]) -> Dict[str, int]:
        """
        CSV 헤더를 데이터베이스 컬럼에 매핑
        
        Args:
            headers: CSV 헤더 목록
            
        Returns:
            Dict[str, int]: 컬럼명과 인덱스 매핑
        """
        column_mapping = {}
        
        for db_column, possible_headers in self.COLUMN_MAPPING.items():
            for i, header in enumerate(headers):
                if header.strip().lower() in [h.lower() for h in possible_headers]:
                    column_mapping[db_column] = i
                    break
        
        # 필수 컬럼 확인
        required_columns = ['location', 'purchase_date', 'model_name', 'name', 'vendor', 'price']
        missing_columns = [col for col in required_columns if col not in column_mapping]
        
        if missing_columns:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_columns}")
        
        return column_mapping
    
    def _parse_row(
        self, 
        row: List[str], 
        column_mapping: Dict[str, int], 
        row_index: int
    ) -> InventoryItemCreate:
        """
        CSV 행을 InventoryItemCreate 객체로 파싱
        
        Args:
            row: CSV 행 데이터
            column_mapping: 컬럼 매핑
            row_index: 행 번호 (오류 메시지용)
            
        Returns:
            InventoryItemCreate: 파싱된 객체
            
        Raises:
            ValueError: 파싱 오류 시
        """
        try:
            data = {}
            
            # 각 필드 파싱
            for field, col_index in column_mapping.items():
                if col_index < len(row):
                    value = row[col_index].strip()
                    data[field] = self._parse_field(field, value, row_index)
                else:
                    if field in ['location', 'purchase_date', 'model_name', 'name', 'vendor', 'price']:
                        raise ValueError(f"필수 필드 '{field}'가 누락되었습니다.")
                    data[field] = None
            
            return InventoryItemCreate(**data)
            
        except Exception as e:
            raise ValueError(f"행 {row_index} 파싱 오류: {e}")
    
    def _parse_field(self, field: str, value: str, row_index: int) -> Any:
        """
        필드별 데이터 파싱
        
        Args:
            field: 필드명
            value: 원본 값
            row_index: 행 번호
            
        Returns:
            Any: 파싱된 값
        """
        if not value:
            if field in ['location', 'purchase_date', 'model_name', 'name', 'vendor', 'price']:
                raise ValueError(f"필수 필드 '{field}'는 비어있을 수 없습니다.")
            return None
        
        try:
            if field in ['purchase_date', 'sale_date']:
                # 날짜 파싱
                for date_format in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        return datetime.strptime(value, date_format).date()
                    except ValueError:
                        continue
                raise ValueError(f"날짜 형식을 인식할 수 없습니다: {value}")
            
            elif field == 'price':
                # 가격 파싱
                # 쉼표 제거 (예: 1,000 -> 1000)
                clean_value = value.replace(',', '').replace('₩', '').replace('원', '')
                return Decimal(clean_value)
            
            elif field in ['location', 'model_name', 'name', 'vendor', 'size', 'notes']:
                # 문자열 필드
                return value.strip()
            
            else:
                return value
                
        except (ValueError, InvalidOperation) as e:
            raise ValueError(f"필드 '{field}' 파싱 오류: {e}")
    
    def _create_error_file(self, original_file: Path, errors: List[Dict]) -> str:
        """
        오류 파일 생성
        
        Args:
            original_file: 원본 파일 경로
            errors: 오류 목록
            
        Returns:
            str: 생성된 오류 파일 경로
        """
        try:
            error_file = original_file.parent / f"import_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(error_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Row', 'Error', 'Data'])
                
                for error in errors:
                    writer.writerow([
                        error['row'],
                        error['error'],
                        str(error['data'])
                    ])
            
            logger.info(f"오류 파일 생성: {error_file}")
            return str(error_file)
            
        except Exception as e:
            logger.error(f"오류 파일 생성 실패: {e}")
            return None
