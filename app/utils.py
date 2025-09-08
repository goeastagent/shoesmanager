"""
유틸리티 함수 모듈

공통으로 사용되는 유틸리티 함수들을 제공합니다.
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    디렉토리가 존재하지 않으면 생성
    
    Args:
        path: 디렉토리 경로
        
    Returns:
        Path: 생성된 디렉토리 경로
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_currency(amount: Union[Decimal, float, int]) -> str:
    """
    통화 형식으로 포맷팅
    
    Args:
        amount: 금액
        
    Returns:
        str: 포맷팅된 통화 문자열
    """
    if amount is None:
        return "₩0"
    
    try:
        amount = float(amount)
        return f"₩{amount:,.0f}"
    except (ValueError, TypeError):
        return "₩0"


def format_date(date_obj: Optional[Union[date, datetime]]) -> str:
    """
    날짜를 문자열로 포맷팅
    
    Args:
        date_obj: 날짜 객체
        
    Returns:
        str: 포맷팅된 날짜 문자열
    """
    if date_obj is None:
        return ""
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(date_obj, date):
        return date_obj.strftime('%Y-%m-%d')
    else:
        return str(date_obj)


def parse_date(date_str: str) -> Optional[date]:
    """
    날짜 문자열을 date 객체로 파싱
    
    Args:
        date_str: 날짜 문자열
        
    Returns:
        Optional[date]: 파싱된 날짜 객체 또는 None
    """
    if not date_str or not date_str.strip():
        return None
    
    date_str = date_str.strip()
    
    # 지원하는 날짜 형식들
    date_formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y.%m.%d',
        '%m.%d.%Y',
        '%d.%m.%Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    logger.warning(f"날짜 형식을 인식할 수 없습니다: {date_str}")
    return None


def parse_decimal(value: Union[str, int, float]) -> Optional[Decimal]:
    """
    값을 Decimal로 파싱
    
    Args:
        value: 파싱할 값
        
    Returns:
        Optional[Decimal]: 파싱된 Decimal 객체 또는 None
    """
    if value is None:
        return None
    
    if isinstance(value, Decimal):
        return value
    
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    
    if isinstance(value, str):
        # 쉼표, 통화 기호 제거
        clean_value = value.replace(',', '').replace('₩', '').replace('원', '').strip()
        if not clean_value:
            return None
        
        try:
            return Decimal(clean_value)
        except (ValueError, TypeError):
            logger.warning(f"Decimal 파싱 실패: {value}")
            return None
    
    return None
