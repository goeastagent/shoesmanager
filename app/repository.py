"""
Repository 패턴 구현

데이터베이스 CRUD 작업과 검색 로직을 캡슐화합니다.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import InventoryItem, Barcode
from app.schemas import (
    InventoryItemCreate, InventoryItemUpdate, SearchQuery, SearchResult,
    BarcodeUpdateRequest
)

logger = logging.getLogger(__name__)


class InventoryRepository:
    """재고 항목 Repository 클래스"""
    
    def __init__(self, session: Session):
        """
        Repository 초기화
        
        Args:
            session: SQLAlchemy 세션 객체
        """
        self.session = session
    
    def create(self, item_data: InventoryItemCreate) -> InventoryItem:
        """
        새로운 재고 항목 생성
        
        Args:
            item_data: 생성할 항목 데이터
            
        Returns:
            InventoryItem: 생성된 항목 객체
            
        Raises:
            SQLAlchemyError: 데이터베이스 오류 시
        """
        try:
            db_item = InventoryItem(**item_data.dict())
            self.session.add(db_item)
            self.session.flush()  # ID 생성을 위해 flush
            self.session.refresh(db_item)
            
            logger.info(f"재고 항목 생성 완료: ID={db_item.id}, 이름={db_item.name}")
            return db_item
            
        except SQLAlchemyError as e:
            logger.error(f"재고 항목 생성 실패: {e}")
            raise
    
    def get_by_id(self, item_id: int) -> Optional[InventoryItem]:
        """
        ID로 재고 항목 조회
        
        Args:
            item_id: 조회할 항목 ID
            
        Returns:
            Optional[InventoryItem]: 조회된 항목 또는 None
        """
        try:
            return self.session.query(InventoryItem).filter(
                InventoryItem.id == item_id
            ).first()
            
        except SQLAlchemyError as e:
            logger.error(f"재고 항목 조회 실패 (ID={item_id}): {e}")
            raise
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[InventoryItem]:
        """
        모든 재고 항목 조회
        
        Args:
            limit: 결과 제한
            offset: 결과 오프셋
            
        Returns:
            List[InventoryItem]: 재고 항목 목록
        """
        try:
            return self.session.query(InventoryItem).offset(offset).limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"재고 항목 목록 조회 실패: {e}")
            raise
    
    def update(self, item_id: int, update_data: InventoryItemUpdate) -> Optional[InventoryItem]:
        """
        재고 항목 수정
        
        Args:
            item_id: 수정할 항목 ID
            update_data: 수정할 데이터
            
        Returns:
            Optional[InventoryItem]: 수정된 항목 또는 None
        """
        try:
            db_item = self.get_by_id(item_id)
            if not db_item:
                return None
            
            # None이 아닌 필드만 업데이트
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(db_item, field, value)
            
            self.session.flush()
            self.session.refresh(db_item)
            
            logger.info(f"재고 항목 수정 완료: ID={item_id}")
            return db_item
            
        except SQLAlchemyError as e:
            logger.error(f"재고 항목 수정 실패 (ID={item_id}): {e}")
            raise
    
    def delete(self, item_id: int) -> bool:
        """
        재고 항목 삭제
        
        Args:
            item_id: 삭제할 항목 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            db_item = self.get_by_id(item_id)
            if not db_item:
                return False
            
            self.session.delete(db_item)
            logger.info(f"재고 항목 삭제 완료: ID={item_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"재고 항목 삭제 실패 (ID={item_id}): {e}")
            raise
    
    def bulk_create(self, items_data: List[InventoryItemCreate]) -> List[InventoryItem]:
        """
        대량 재고 항목 생성
        
        Args:
            items_data: 생성할 항목 데이터 목록
            
        Returns:
            List[InventoryItem]: 생성된 항목 목록
        """
        try:
            db_items = [InventoryItem(**item.dict()) for item in items_data]
            self.session.add_all(db_items)
            self.session.flush()
            
            # 생성된 ID들을 위해 refresh
            for item in db_items:
                self.session.refresh(item)
            
            logger.info(f"대량 재고 항목 생성 완료: {len(db_items)}개")
            return db_items
            
        except SQLAlchemyError as e:
            logger.error(f"대량 재고 항목 생성 실패: {e}")
            raise
    
    def bulk_delete(self, item_ids: List[int]) -> int:
        """
        대량 재고 항목 삭제
        
        Args:
            item_ids: 삭제할 항목 ID 목록
            
        Returns:
            int: 삭제된 항목 수
        """
        try:
            deleted_count = self.session.query(InventoryItem).filter(
                InventoryItem.id.in_(item_ids)
            ).delete(synchronize_session=False)
            
            logger.info(f"대량 재고 항목 삭제 완료: {deleted_count}개")
            return deleted_count
            
        except SQLAlchemyError as e:
            logger.error(f"대량 재고 항목 삭제 실패: {e}")
            raise
    
    def search(self, query: SearchQuery) -> SearchResult:
        """
        재고 항목 검색
        
        Args:
            query: 검색 쿼리 객체
            
        Returns:
            SearchResult: 검색 결과
        """
        try:
            # 기본 쿼리
            db_query = self.session.query(InventoryItem)
            
            # 필터 조건 추가
            filters = []
            
            # 키워드 검색 (SQLite용 LIKE 검색)
            if query.keyword:
                keyword_pattern = f"%{query.keyword}%"
                keyword_filter = or_(
                    InventoryItem.name.like(keyword_pattern),
                    InventoryItem.model_name.like(keyword_pattern),
                    InventoryItem.vendor.like(keyword_pattern),
                    InventoryItem.notes.like(keyword_pattern)
                )
                filters.append(keyword_filter)
            
            # 개별 필드 검색
            if query.location:
                filters.append(InventoryItem.location.like(f"%{query.location}%"))
            
            if query.model_name:
                filters.append(InventoryItem.model_name.like(f"%{query.model_name}%"))
            
            if query.name:
                filters.append(InventoryItem.name.like(f"%{query.name}%"))
            
            if query.vendor:
                filters.append(InventoryItem.vendor.like(f"%{query.vendor}%"))
            
            if query.size:
                filters.append(InventoryItem.size.like(f"%{query.size}%"))
            
            if query.barcode:
                filters.append(InventoryItem.barcode.like(f"%{query.barcode}%"))
            
            # 날짜 범위 검색
            if query.purchase_date_from:
                filters.append(InventoryItem.purchase_date >= query.purchase_date_from)
            
            if query.purchase_date_to:
                filters.append(InventoryItem.purchase_date <= query.purchase_date_to)
            
            if query.sale_date_from:
                filters.append(InventoryItem.sale_date >= query.sale_date_from)
            
            if query.sale_date_to:
                filters.append(InventoryItem.sale_date <= query.sale_date_to)
            
            # 가격 범위 검색
            if query.price_min is not None:
                filters.append(InventoryItem.price >= query.price_min)
            
            if query.price_max is not None:
                filters.append(InventoryItem.price <= query.price_max)
            
            # 필터 적용
            if filters:
                db_query = db_query.filter(and_(*filters))
            
            # 전체 개수 조회
            total_count = db_query.count()
            
            # 정렬
            sort_column = getattr(InventoryItem, query.sort_by)
            if query.sort_desc:
                db_query = db_query.order_by(sort_column.desc())
            else:
                db_query = db_query.order_by(sort_column.asc())
            
            # 페이징
            items = db_query.offset(query.offset).limit(query.limit).all()
            
            # 결과 생성
            result = SearchResult(
                items=items,
                total_count=total_count,
                limit=query.limit,
                offset=query.offset,
                has_more=(query.offset + len(items)) < total_count
            )
            
            logger.info(f"검색 완료: {len(items)}개 결과, 전체 {total_count}개")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"검색 실패: {e}")
            raise
    
    def get_statistics(self) -> dict:
        """
        재고 통계 조회
        
        Returns:
            dict: 통계 정보
        """
        try:
            stats = {}
            
            # 전체 항목 수
            stats['total_items'] = self.session.query(InventoryItem).count()
            
            # 판매된 항목 수
            stats['sold_items'] = self.session.query(InventoryItem).filter(
                InventoryItem.sale_date.isnot(None)
            ).count()
            
            # 재고 항목 수
            stats['in_stock_items'] = stats['total_items'] - stats['sold_items']
            
            # 총 가치 (재고 항목만)
            total_value = self.session.query(func.sum(InventoryItem.price)).filter(
                InventoryItem.sale_date.is_(None)
            ).scalar()
            stats['total_value'] = float(total_value) if total_value else 0.0
            
            # 평균 가격
            avg_price = self.session.query(func.avg(InventoryItem.price)).scalar()
            stats['average_price'] = float(avg_price) if avg_price else 0.0
            
            # 최고/최저 가격
            max_price = self.session.query(func.max(InventoryItem.price)).scalar()
            min_price = self.session.query(func.min(InventoryItem.price)).scalar()
            stats['max_price'] = float(max_price) if max_price else 0.0
            stats['min_price'] = float(min_price) if min_price else 0.0
            
            logger.info("통계 조회 완료")
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"통계 조회 실패: {e}")
            raise
    
    def get_vendors(self) -> List[str]:
        """
        구매처 목록 조회
        
        Returns:
            List[str]: 구매처 목록
        """
        try:
            vendors = self.session.query(InventoryItem.vendor).distinct().all()
            return [vendor[0] for vendor in vendors if vendor[0]]
            
        except SQLAlchemyError as e:
            logger.error(f"구매처 목록 조회 실패: {e}")
            raise
    
    def get_locations(self) -> List[str]:
        """
        위치 목록 조회
        
        Returns:
            List[str]: 위치 목록
        """
        try:
            locations = self.session.query(InventoryItem.location).distinct().all()
            return [location[0] for location in locations if location[0]]
            
        except SQLAlchemyError as e:
            logger.error(f"위치 목록 조회 실패: {e}")
            raise
    
    def create_or_update_barcode(self, barcode: str, model_name: str, name: str) -> Barcode:
        """
        바코드 정보 생성 또는 업데이트
        
        동일한 바코드로 다른 제품명/모델명이 입력되면 기존 정보를 덮어씁니다.
        
        Args:
            barcode: 바코드
            model_name: 모델명
            name: 제품명
            
        Returns:
            Barcode: 생성되거나 업데이트된 바코드 객체
        """
        try:
            # 기존 바코드 조회
            existing_barcode = self.session.query(Barcode).filter(
                Barcode.barcode == barcode
            ).first()
            
            if existing_barcode:
                # 기존 바코드가 있으면 업데이트
                existing_barcode.model_name = model_name
                existing_barcode.name = name
                self.session.flush()
                self.session.refresh(existing_barcode)
                
                logger.info(f"바코드 정보 업데이트: {barcode} -> {name} ({model_name})")
                return existing_barcode
            else:
                # 새로운 바코드 생성
                new_barcode = Barcode(
                    barcode=barcode,
                    model_name=model_name,
                    name=name
                )
                self.session.add(new_barcode)
                self.session.flush()
                self.session.refresh(new_barcode)
                
                logger.info(f"새 바코드 정보 생성: {barcode} -> {name} ({model_name})")
                return new_barcode
                
        except SQLAlchemyError as e:
            logger.error(f"바코드 정보 생성/업데이트 실패 ({barcode}): {e}")
            raise
    
    def get_barcode_info(self, barcode: str) -> Optional[Barcode]:
        """
        바코드 정보 조회
        
        Args:
            barcode: 조회할 바코드
            
        Returns:
            Optional[Barcode]: 바코드 정보 또는 None
        """
        try:
            return self.session.query(Barcode).filter(
                Barcode.barcode == barcode
            ).first()
            
        except SQLAlchemyError as e:
            logger.error(f"바코드 정보 조회 실패 ({barcode}): {e}")
            raise
    
    def get_latest_inventory_by_barcode(self, barcode: str) -> Optional[InventoryItem]:
        """
        바코드로 가장 최근의 재고 항목 조회
        
        Args:
            barcode: 조회할 바코드
            
        Returns:
            Optional[InventoryItem]: 가장 최근의 재고 항목 또는 None
        """
        try:
            return self.session.query(InventoryItem).filter(
                InventoryItem.barcode == barcode
            ).order_by(InventoryItem.created_at.desc()).first()
            
        except SQLAlchemyError as e:
            logger.error(f"바코드로 재고 항목 조회 실패 ({barcode}): {e}")
            raise
    
    def create_with_barcode_update(self, item_data: InventoryItemCreate) -> InventoryItem:
        """
        재고 항목 생성 시 바코드 정보도 함께 업데이트
        
        Args:
            item_data: 생성할 항목 데이터
            
        Returns:
            InventoryItem: 생성된 항목 객체
        """
        try:
            # 재고 항목 생성
            db_item = self.create(item_data)
            
            # 바코드가 있으면 바코드 테이블도 업데이트
            if item_data.barcode:
                self.create_or_update_barcode(
                    barcode=item_data.barcode,
                    model_name=item_data.model_name,
                    name=item_data.name
                )
            
            return db_item
            
        except SQLAlchemyError as e:
            logger.error(f"바코드 업데이트와 함께 재고 항목 생성 실패: {e}")
            raise
    
    def get_inventory_by_barcode(self, barcode: str) -> List[InventoryItem]:
        """
        바코드로 재고 항목들 조회 (판매되지 않은 항목만)
        
        Args:
            barcode: 조회할 바코드
            
        Returns:
            List[InventoryItem]: 재고 항목 목록
        """
        try:
            return self.session.query(InventoryItem).filter(
                InventoryItem.barcode == barcode,
                InventoryItem.sale_date.is_(None)  # 판매되지 않은 항목만
            ).order_by(InventoryItem.created_at.desc()).all()
            
        except SQLAlchemyError as e:
            logger.error(f"바코드로 재고 항목 조회 실패 ({barcode}): {e}")
            raise
    
    def sell_item(self, item_id: str, sale_date: date) -> bool:
        """
        재고 항목 판매 처리
        
        Args:
            item_id: 판매할 항목 ID
            sale_date: 판매일
            
        Returns:
            bool: 판매 성공 여부
        """
        try:
            db_item = self.get_by_id(item_id)
            if not db_item:
                return False
            
            # 이미 판매된 항목인지 확인
            if db_item.sale_date:
                return False
            
            # 판매일 설정
            db_item.sale_date = sale_date
            self.session.flush()
            self.session.refresh(db_item)
            
            logger.info(f"재고 항목 판매 완료: ID={item_id}, 판매일={sale_date}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"재고 항목 판매 실패 (ID={item_id}): {e}")
            raise
