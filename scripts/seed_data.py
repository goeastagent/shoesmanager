#!/usr/bin/env python3
"""
시드 데이터 생성 스크립트

데이터베이스에 샘플 데이터를 생성합니다.
"""

import sys
import os
import logging
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import setup_logging
from app.db import db_manager, check_database_connection
from app.repository import InventoryRepository
from app.schemas import InventoryItemCreate

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)


def create_sample_data():
    """샘플 데이터 생성"""
    
    # 데이터베이스 연결 확인
    if not check_database_connection():
        print("❌ 데이터베이스 연결에 실패했습니다.")
        return False
    
    print("✅ 데이터베이스 연결 성공")
    
    # 샘플 데이터 정의
    sample_items = [
        {
            'location': 'A-01',
            'purchase_date': date(2024, 1, 1),
            'sale_date': None,
            'model_name': 'Nike Air Max',
            'name': 'Nike Air Max 270',
            'size': '270',
            'vendor': 'ABC몰',
            'price': Decimal('129000'),
            'notes': '인기 상품, 빠른 판매 예상'
        },
        {
            'location': 'A-02',
            'purchase_date': date(2024, 1, 2),
            'sale_date': date(2024, 1, 15),
            'model_name': 'Adidas Ultraboost',
            'name': 'Adidas Ultraboost 22',
            'size': '280',
            'vendor': 'XYZ스토어',
            'price': Decimal('159000'),
            'notes': '이미 판매됨'
        },
        {
            'location': 'A-03',
            'purchase_date': date(2024, 1, 3),
            'sale_date': None,
            'model_name': 'Converse Chuck',
            'name': 'Converse Chuck Taylor All Star',
            'size': '260',
            'vendor': 'ABC몰',
            'price': Decimal('89000'),
            'notes': '클래식 디자인'
        },
        {
            'location': 'B-01',
            'purchase_date': date(2024, 1, 5),
            'sale_date': None,
            'model_name': 'New Balance',
            'name': 'New Balance 990v5',
            'size': '275',
            'vendor': 'DEF쇼핑몰',
            'price': Decimal('189000'),
            'notes': '프리미엄 라인'
        },
        {
            'location': 'B-02',
            'purchase_date': date(2024, 1, 7),
            'sale_date': date(2024, 1, 20),
            'model_name': 'Vans Old Skool',
            'name': 'Vans Old Skool Classic',
            'size': '265',
            'vendor': 'XYZ스토어',
            'price': Decimal('79000'),
            'notes': '스케이트보드 신발'
        },
        {
            'location': 'B-03',
            'purchase_date': date(2024, 1, 10),
            'sale_date': None,
            'model_name': 'Puma Suede',
            'name': 'Puma Suede Classic',
            'size': '270',
            'vendor': 'GHI스포츠',
            'price': Decimal('99000'),
            'notes': '레트로 스타일'
        },
        {
            'location': 'C-01',
            'purchase_date': date(2024, 1, 12),
            'sale_date': None,
            'model_name': 'Reebok Classic',
            'name': 'Reebok Classic Leather',
            'size': '280',
            'vendor': 'ABC몰',
            'price': Decimal('119000'),
            'notes': '빈티지 컬렉션'
        },
        {
            'location': 'C-02',
            'purchase_date': date(2024, 1, 15),
            'sale_date': date(2024, 1, 25),
            'model_name': 'Jordan 1',
            'name': 'Air Jordan 1 Retro High',
            'size': '275',
            'vendor': 'JKL스니커즈',
            'price': Decimal('199000'),
            'notes': '한정판, 빠른 판매'
        },
        {
            'location': 'C-03',
            'purchase_date': date(2024, 1, 18),
            'sale_date': None,
            'model_name': 'Asics Gel',
            'name': 'Asics Gel-Kayano 28',
            'size': '270',
            'vendor': 'MNO런닝',
            'price': Decimal('179000'),
            'notes': '런닝 전문 신발'
        },
        {
            'location': 'D-01',
            'purchase_date': date(2024, 1, 20),
            'sale_date': None,
            'model_name': 'Under Armour',
            'name': 'Under Armour Charged Assert 9',
            'size': '275',
            'vendor': 'PQR피트니스',
            'price': Decimal('139000'),
            'notes': '운동용 신발'
        },
        {
            'location': 'D-02',
            'purchase_date': date(2024, 1, 22),
            'sale_date': None,
            'model_name': 'Saucony',
            'name': 'Saucony Jazz Original',
            'size': '265',
            'vendor': 'STU클래식',
            'price': Decimal('109000'),
            'notes': '오리지널 디자인'
        },
        {
            'location': 'D-03',
            'purchase_date': date(2024, 1, 25),
            'sale_date': date(2024, 2, 1),
            'model_name': 'Brooks',
            'name': 'Brooks Ghost 14',
            'size': '280',
            'vendor': 'VWX마라톤',
            'price': Decimal('169000'),
            'notes': '마라톤 전문 신발'
        },
        {
            'location': 'E-01',
            'purchase_date': date(2024, 1, 28),
            'sale_date': None,
            'model_name': 'Hoka One One',
            'name': 'Hoka One One Bondi 7',
            'size': '270',
            'vendor': 'YZA트레일',
            'price': Decimal('189000'),
            'notes': '쿠셔닝 최고'
        },
        {
            'location': 'E-02',
            'purchase_date': date(2024, 2, 1),
            'sale_date': None,
            'model_name': 'Salomon',
            'name': 'Salomon Speedcross 5',
            'size': '275',
            'vendor': 'BCD아웃도어',
            'price': Decimal('199000'),
            'notes': '트레일 러닝'
        },
        {
            'location': 'E-03',
            'purchase_date': date(2024, 2, 3),
            'sale_date': None,
            'model_name': 'Merrell',
            'name': 'Merrell Moab 2 Vent',
            'size': '280',
            'vendor': 'EFG하이킹',
            'price': Decimal('149000'),
            'notes': '하이킹 부츠'
        }
    ]
    
    try:
        print(f"📦 {len(sample_items)}개의 샘플 데이터 생성 중...")
        
        # 세션 컨텍스트 매니저 사용
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            
            created_count = 0
            for i, item_data in enumerate(sample_items, 1):
                try:
                    item = InventoryItemCreate(**item_data)
                    created_item = repository.create(item)
                    created_count += 1
                    print(f"  ✅ {i:2d}. {created_item.name} (ID: {created_item.id})")
                except Exception as e:
                    print(f"  ❌ {i:2d}. {item_data['name']} 생성 실패: {e}")
            
            print(f"\n🎉 샘플 데이터 생성 완료: {created_count}/{len(sample_items)}개 성공")
            
            # 통계 출력
            stats = repository.get_statistics()
            print(f"\n📊 현재 재고 통계:")
            print(f"  • 전체 항목: {stats['total_items']:,}개")
            print(f"  • 재고 항목: {stats['in_stock_items']:,}개")
            print(f"  • 판매된 항목: {stats['sold_items']:,}개")
            print(f"  • 총 재고 가치: ₩{stats['total_value']:,.0f}")
            print(f"  • 평균 가격: ₩{stats['average_price']:,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 샘플 데이터 생성 실패: {e}")
        return False


def clear_all_data():
    """모든 데이터 삭제"""
    try:
        print("🗑️  모든 데이터 삭제 중...")
        
        repository = InventoryRepository(db_manager.get_session())
        
        # 모든 항목 조회
        all_items = repository.get_all(limit=10000)
        
        if not all_items:
            print("  삭제할 데이터가 없습니다.")
            return True
        
        # 모든 항목 삭제
        item_ids = [item.id for item in all_items]
        deleted_count = repository.bulk_delete(item_ids)
        
        print(f"  ✅ {deleted_count}개 항목 삭제 완료")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 삭제 실패: {e}")
        return False


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="시드 데이터 생성 스크립트")
    parser.add_argument("--clear", action="store_true", help="기존 데이터 삭제")
    parser.add_argument("--force", action="store_true", help="확인 없이 실행")
    
    args = parser.parse_args()
    
    if args.clear:
        if not args.force:
            response = input("정말로 모든 데이터를 삭제하시겠습니까? (y/N): ")
            if response.lower() != 'y':
                print("취소되었습니다.")
                return
        
        if clear_all_data():
            print("데이터 삭제가 완료되었습니다.")
        else:
            print("데이터 삭제에 실패했습니다.")
            return
    
    if create_sample_data():
        print("\n✨ 시드 데이터 생성이 완료되었습니다!")
        print("\n다음 명령어로 데이터를 확인할 수 있습니다:")
        print("  python -m app.ui.cli list")
        print("  python -m app.ui.cli stats")
        print("  python -m app.ui.tk_app")
    else:
        print("\n❌ 시드 데이터 생성에 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
