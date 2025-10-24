"""
FastAPI 웹 애플리케이션

물류 관리 시스템의 웹 인터페이스를 제공합니다.
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import setup_logging, settings
from app.db import db_manager, check_database_connection
from app.repository import InventoryRepository
from app.schemas import (
    InventoryItemCreate, InventoryItemUpdate, SearchQuery, 
    InventoryItemResponse, SearchResult
)

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="물류 관리 시스템",
    description="신발 재고 관리를 위한 웹 애플리케이션",
    version="1.0.0"
)

# 템플릿 및 정적 파일 경로 설정
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("웹 애플리케이션 시작")
    if not check_database_connection():
        logger.error("데이터베이스 연결 실패")
        raise Exception("데이터베이스 연결에 실패했습니다.")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("웹 애플리케이션 종료")
    db_manager.close()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/items", response_model=SearchResult)
async def search_items(
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    model_name: Optional[str] = None,
    name: Optional[str] = None,
    vendor: Optional[str] = None,
    size: Optional[str] = None,
    barcode: Optional[str] = None,
    purchase_date_from: Optional[str] = None,
    purchase_date_to: Optional[str] = None,
    sale_date_from: Optional[str] = None,
    sale_date_to: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort_by: str = "created_at",
    sort_desc: bool = True,
    page: int = 1,
    page_size: int = 50
):
    """재고 항목 검색"""
    try:
        # 날짜 파싱
        def parse_date(date_str: Optional[str]) -> Optional[date]:
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None
        
        # 검색 쿼리 구성
        search_query = SearchQuery(
            keyword=keyword or None,
            location=location or None,
            model_name=model_name or None,
            name=name or None,
            vendor=vendor or None,
            size=size or None,
            barcode=barcode or None,
            purchase_date_from=parse_date(purchase_date_from),
            purchase_date_to=parse_date(purchase_date_to),
            sale_date_from=parse_date(sale_date_from),
            sale_date_to=parse_date(sale_date_to),
            price_min=Decimal(str(price_min)) if price_min is not None else None,
            price_max=Decimal(str(price_max)) if price_max is not None else None,
            sort_by=sort_by,
            sort_desc=sort_desc,
            limit=page_size,
            offset=(page - 1) * page_size
        )
        
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            result = repository.search(search_query)
        
        return result
        
    except Exception as e:
        logger.error(f"검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/items/{item_id}", response_model=InventoryItemResponse)
async def get_item(item_id: str):
    """재고 항목 상세 조회"""
    try:
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            item = repository.get_by_id(item_id)
            
            if not item:
                raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
            
            return item
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"항목 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/items", response_model=InventoryItemResponse)
async def create_item(item: InventoryItemCreate):
    """새 재고 항목 추가"""
    try:
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            new_item = repository.create_with_barcode_update(item)
            
        return new_item
        
    except Exception as e:
        logger.error(f"항목 추가 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/items/{item_id}", response_model=InventoryItemResponse)
async def update_item(item_id: str, item: InventoryItemUpdate):
    """재고 항목 수정"""
    try:
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            updated_item = repository.update(item_id, item)
            
            if not updated_item:
                raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
            
        return updated_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"항목 수정 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/items/{item_id}")
async def delete_item(item_id: str):
    """재고 항목 삭제"""
    try:
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            success = repository.delete(item_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
            
        return {"message": "삭제되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"항목 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/items/{item_id}/sell")
async def sell_item(item_id: str, sale_date: Optional[str] = None):
    """재고 항목 판매 처리"""
    try:
        # 날짜 파싱
        parsed_date = date.today()
        if sale_date:
            try:
                parsed_date = datetime.strptime(sale_date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다.")
        
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            success = repository.sell_item(item_id, parsed_date)
            
            if not success:
                raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
            
        return {"message": "판매 처리되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"판매 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/items/barcode/{barcode}")
async def get_items_by_barcode(barcode: str):
    """바코드로 재고 항목 조회"""
    try:
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            items = repository.get_inventory_by_barcode(barcode)
            
        return {"items": items, "count": len(items)}
        
    except Exception as e:
        logger.error(f"바코드 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/barcode-info/{barcode}")
async def get_barcode_info(barcode: str):
    """바코드 정보 조회 (자동완성용)"""
    try:
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            item = repository.get_latest_inventory_by_barcode(barcode)
            
            if not item:
                return {"found": False}
            
            return {
                "found": True,
                "model_name": item.model_name,
                "name": item.name,
                "size": item.size,
                "price": str(item.price),
                "vendor": item.vendor
            }
            
    except Exception as e:
        logger.error(f"바코드 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/filters")
async def get_filters():
    """필터 옵션 조회 (위치, 구매처 목록)"""
    try:
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            locations = repository.get_locations()
            vendors = repository.get_vendors()
            
        return {
            "locations": locations,
            "vendors": vendors
        }
        
    except Exception as e:
        logger.error(f"필터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """메인 함수 - 개발 서버 실행"""
    import uvicorn
    
    logger.info("웹 서버 시작 중...")
    uvicorn.run(
        "app.ui.web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

