"""
Pydantic 스키마 정의

데이터 검증, 직렬화, API 요청/응답 모델을 정의합니다.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class InventoryItemBase(BaseModel):
    """재고 항목 기본 스키마"""
    
    location: str = Field(..., min_length=1, max_length=50, description="보관 위치")
    purchase_date: date = Field(..., description="구매일")
    sale_date: Optional[date] = Field(None, description="판매일")
    model_name: str = Field(..., min_length=1, max_length=100, description="모델명")
    name: str = Field(..., min_length=1, max_length=100, description="제품명")
    size: Optional[str] = Field(None, max_length=20, description="사이즈")
    vendor: str = Field(..., min_length=1, max_length=100, description="구매처")
    price: Decimal = Field(..., ge=0, decimal_places=2, description="가격")
    notes: Optional[str] = Field(None, description="메모")
    
    @field_validator('location', 'model_name', 'name', 'vendor')
    @classmethod
    def validate_required_fields(cls, v):
        """필수 필드 검증: 공백 불가"""
        if not v or not v.strip():
            raise ValueError('필수 필드는 공백일 수 없습니다.')
        return v.strip()
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        """사이즈 검증: 공백 제거"""
        if v is not None:
            return v.strip() if v.strip() else None
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """날짜 검증: 구매일이 판매일보다 늦을 수 없음"""
        if self.purchase_date and self.sale_date and self.sale_date < self.purchase_date:
            raise ValueError('판매일은 구매일보다 늦어야 합니다.')
        return self


class InventoryItemCreate(InventoryItemBase):
    """재고 항목 생성 스키마"""
    pass


class InventoryItemUpdate(BaseModel):
    """재고 항목 수정 스키마"""
    
    location: Optional[str] = Field(None, min_length=1, max_length=50, description="보관 위치")
    purchase_date: Optional[date] = Field(None, description="구매일")
    sale_date: Optional[date] = Field(None, description="판매일")
    model_name: Optional[str] = Field(None, min_length=1, max_length=100, description="모델명")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="제품명")
    size: Optional[str] = Field(None, max_length=20, description="사이즈")
    vendor: Optional[str] = Field(None, min_length=1, max_length=100, description="구매처")
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="가격")
    notes: Optional[str] = Field(None, description="메모")
    
    @field_validator('location', 'model_name', 'name', 'vendor')
    @classmethod
    def validate_required_fields(cls, v):
        """필수 필드 검증: 공백 불가"""
        if v is not None and (not v or not v.strip()):
            raise ValueError('필수 필드는 공백일 수 없습니다.')
        return v.strip() if v else v
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        """사이즈 검증: 공백 제거"""
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class InventoryItemResponse(InventoryItemBase):
    """재고 항목 응답 스키마"""
    
    id: str = Field(..., description="고유 식별자 (UUID)")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    
    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    """검색 쿼리 스키마"""
    
    # 키워드 검색
    keyword: Optional[str] = Field(None, description="전체 텍스트 검색 키워드")
    
    # 개별 필드 검색
    location: Optional[str] = Field(None, description="위치")
    model_name: Optional[str] = Field(None, description="모델명")
    name: Optional[str] = Field(None, description="제품명")
    vendor: Optional[str] = Field(None, description="구매처")
    size: Optional[str] = Field(None, description="사이즈")
    
    # 날짜 범위 검색
    purchase_date_from: Optional[date] = Field(None, description="구매일 시작")
    purchase_date_to: Optional[date] = Field(None, description="구매일 종료")
    sale_date_from: Optional[date] = Field(None, description="판매일 시작")
    sale_date_to: Optional[date] = Field(None, description="판매일 종료")
    
    # 가격 범위 검색
    price_min: Optional[Decimal] = Field(None, ge=0, description="최소 가격")
    price_max: Optional[Decimal] = Field(None, ge=0, description="최대 가격")
    
    # 정렬 및 페이징
    sort_by: Literal["id", "location", "purchase_date", "sale_date", "model_name", "name", "size", "vendor", "price", "created_at"] = Field(
        default="created_at", description="정렬 기준"
    )
    sort_desc: bool = Field(default=True, description="내림차순 정렬")
    limit: int = Field(default=100, ge=1, le=10000, description="결과 제한")
    offset: int = Field(default=0, ge=0, description="결과 오프셋")
    
    @model_validator(mode='after')
    def validate_date_ranges(self):
        """날짜 및 가격 범위 검증"""
        # 구매일 범위 검증
        if self.purchase_date_from and self.purchase_date_to and self.purchase_date_from > self.purchase_date_to:
            raise ValueError('구매일 시작일은 종료일보다 늦을 수 없습니다.')
        
        # 판매일 범위 검증
        if self.sale_date_from and self.sale_date_to and self.sale_date_from > self.sale_date_to:
            raise ValueError('판매일 시작일은 종료일보다 늦을 수 없습니다.')
        
        # 가격 범위 검증
        if self.price_min and self.price_max and self.price_min > self.price_max:
            raise ValueError('최소 가격은 최대 가격보다 클 수 없습니다.')
        
        return self


class SearchResult(BaseModel):
    """검색 결과 스키마"""
    
    items: List[InventoryItemResponse] = Field(..., description="검색 결과 항목들")
    total_count: int = Field(..., description="전체 결과 수")
    limit: int = Field(..., description="결과 제한")
    offset: int = Field(..., description="결과 오프셋")
    has_more: bool = Field(..., description="더 많은 결과 존재 여부")


class BulkCreateRequest(BaseModel):
    """대량 생성 요청 스키마"""
    
    items: List[InventoryItemCreate] = Field(..., min_items=1, max_items=1000, description="생성할 항목들")


class BulkUpdateRequest(BaseModel):
    """대량 수정 요청 스키마"""
    
    updates: List[dict] = Field(..., min_items=1, max_items=100, description="수정할 항목들 (id 포함)")


class BulkDeleteRequest(BaseModel):
    """대량 삭제 요청 스키마"""
    
    ids: List[int] = Field(..., min_items=1, max_items=100, description="삭제할 항목 ID들")


class ImportResult(BaseModel):
    """CSV 가져오기 결과 스키마"""
    
    success_count: int = Field(..., description="성공한 항목 수")
    error_count: int = Field(..., description="실패한 항목 수")
    errors: List[dict] = Field(..., description="오류 상세 정보")
    error_file_path: Optional[str] = Field(None, description="오류 파일 경로")


class ExportRequest(BaseModel):
    """내보내기 요청 스키마"""
    
    search_query: Optional[SearchQuery] = Field(None, description="검색 조건")
    format: Literal["csv", "html"] = Field(default="csv", description="내보내기 형식")
    include_headers: bool = Field(default=True, description="헤더 포함 여부")
