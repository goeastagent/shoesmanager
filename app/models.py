"""
SQLAlchemy 데이터베이스 모델 정의

물류 관리 시스템의 핵심 엔티티인 InventoryItem 모델을 정의합니다.
"""

from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy import (
    Column, String, Date, DateTime, Text, 
    DECIMAL, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates

Base = declarative_base()


class InventoryItem(Base):
    """
    재고 항목 모델
    
    신발 관리 시스템의 핵심 엔티티로, 각 신발 항목의 정보를 저장합니다.
    """
    
    __tablename__ = 'inventory_items'
    
    # 기본 키 (UUID 사용)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="고유 식별자 (UUID)")
    
    # 필수 필드
    location = Column(String(50), nullable=False, comment="보관 위치")
    purchase_date = Column(Date, nullable=False, comment="구매일")
    model_name = Column(String(100), nullable=False, comment="모델명")
    name = Column(String(100), nullable=False, comment="제품명")
    vendor = Column(String(100), nullable=False, comment="구매처")
    price = Column(DECIMAL(12, 2), nullable=False, comment="가격")
    
    # 선택적 필드
    sale_date = Column(Date, nullable=True, comment="판매일")
    size = Column(String(20), nullable=True, comment="사이즈")
    notes = Column(Text, nullable=True, comment="메모")
    
    # 시스템 필드
    created_at = Column(DateTime, nullable=False, default=func.now(), comment="생성일시")
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment="수정일시")
    
    # 인덱스 정의
    __table_args__ = (
        # BTREE 인덱스
        Index('idx_model_name', 'model_name', 'name'),
        Index('idx_sale_date', 'sale_date'),
        
        # FULLTEXT 인덱스 (검색 최적화)
        Index('idx_fulltext_search', 'name', 'model_name', 'vendor', 'notes', mysql_prefix='FULLTEXT'),
    )
    
    @validates('price')
    def validate_price(self, key, price):
        """가격 검증: 0 이상이어야 함"""
        if price is not None and price < 0:
            raise ValueError("가격은 0 이상이어야 합니다.")
        return price
    
    @validates('purchase_date', 'sale_date')
    def validate_dates(self, key, date_value):
        """날짜 검증: 구매일이 판매일보다 늦을 수 없음"""
        if key == 'sale_date' and date_value is not None:
            if self.purchase_date and date_value < self.purchase_date:
                raise ValueError("판매일은 구매일보다 늦어야 합니다.")
        return date_value
    
    @validates('location', 'model_name', 'name', 'vendor')
    def validate_required_fields(self, key, value):
        """필수 필드 검증: 공백 불가"""
        if not value or not value.strip():
            raise ValueError(f"{key}는 필수 필드이며 공백일 수 없습니다.")
        return value.strip()
    
    @validates('size')
    def validate_size(self, key, size):
        """사이즈 검증: 공백 제거"""
        if size is not None:
            return size.strip() if size.strip() else None
        return size
    
    def __repr__(self) -> str:
        """객체 문자열 표현"""
        return (
            f"<InventoryItem(id={self.id}, name='{self.name}', "
            f"model='{self.model_name}', location='{self.location}', "
            f"price={self.price})>"
        )
    
    def to_dict(self) -> dict:
        """
        객체를 딕셔너리로 변환
        
        Returns:
            dict: 객체의 속성을 담은 딕셔너리
        """
        return {
            'id': self.id,
            'location': self.location,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'model_name': self.model_name,
            'name': self.name,
            'size': self.size,
            'vendor': self.vendor,
            'price': float(self.price) if self.price else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InventoryItem':
        """
        딕셔너리에서 객체 생성
        
        Args:
            data: 객체 속성을 담은 딕셔너리
            
        Returns:
            InventoryItem: 생성된 객체
        """
        # 날짜 문자열을 date 객체로 변환
        if 'purchase_date' in data and isinstance(data['purchase_date'], str):
            data['purchase_date'] = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
        
        if 'sale_date' in data and isinstance(data['sale_date'], str):
            data['sale_date'] = datetime.strptime(data['sale_date'], '%Y-%m-%d').date()
        
        # Decimal 변환
        if 'price' in data and isinstance(data['price'], (int, float)):
            data['price'] = Decimal(str(data['price']))
        
        return cls(**data)
