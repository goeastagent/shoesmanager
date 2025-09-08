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

from app.models import InventoryItem
from app.schemas import (
    InventoryItemCreate, InventoryItemUpdate, SearchQuery, SearchResult
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
