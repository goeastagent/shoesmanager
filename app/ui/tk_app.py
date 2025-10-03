"""
Tkinter GUI 애플리케이션

물류 관리 시스템의 그래픽 사용자 인터페이스를 제공합니다.
"""

import logging
import threading
import tkinter as tk
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List

from app.config import setup_logging, settings
from app.db import db_manager, check_database_connection
from app.repository import InventoryRepository
from app.schemas import (
    InventoryItemCreate, InventoryItemUpdate, SearchQuery, InventoryItemResponse
)
from app.services.import_service import CSVImportService
from app.services.export_service import ExportService

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)


class InventoryApp:
    """재고 관리 GUI 애플리케이션"""
    
    def __init__(self):
        """애플리케이션 초기화"""
        self.root = tk.Tk()
        self.root.title("물류 관리 시스템")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # 데이터베이스 연결 확인
        if not check_database_connection():
            messagebox.showerror("오류", "데이터베이스 연결에 실패했습니다.")
            self.root.quit()
            return
        
        # Repository 및 서비스 초기화 (세션은 각 작업마다 새로 생성)
        self.import_service = None  # 나중에 초기화
        self.export_service = None  # 나중에 초기화
        
        # 현재 선택된 항목
        self.selected_item: Optional[InventoryItemResponse] = None
        
        # 정렬 관련 변수
        self.sort_column = "created_at"  # 기본 정렬 컬럼
        self.sort_desc = True  # 기본 정렬 방향 (내림차순)
        
        # UI 구성
        self.setup_ui()
        self.refresh_data()
        
        # 창 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 메뉴바 생성
        self.create_menu()
        
        # 툴바 생성
        self.create_toolbar(main_frame)
        
        # 상단 검색 패널
        self.create_search_panel(main_frame)
        
        # 중앙 패널 (목록과 상세 정보)
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 목록 패널
        self.create_list_panel(center_frame)
        
        # 상세 정보 패널
        self.create_detail_panel(center_frame)
        
        # 하단 상태바
        self.create_status_bar(main_frame)
    
    def create_menu(self):
        """메뉴바 생성"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="CSV 가져오기", command=self.import_csv)
        file_menu.add_command(label="CSV 내보내기", command=self.export_csv)
        file_menu.add_command(label="HTML 내보내기", command=self.export_html)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.on_closing)
        
        # 편집 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="편집", menu=edit_menu)
        edit_menu.add_command(label="새 항목 추가", command=self.add_item)
        edit_menu.add_command(label="선택 항목 수정", command=self.edit_item)
        edit_menu.add_command(label="선택 항목 삭제", command=self.delete_item)
        edit_menu.add_separator()
        edit_menu.add_command(label="바코드로 판매", command=self.sell_by_barcode)
        
        # 보기 메뉴
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="보기", menu=view_menu)
        view_menu.add_command(label="새로고침", command=self.refresh_data)
        view_menu.add_command(label="통계 보기", command=self.show_statistics)
    
    def create_toolbar(self, parent):
        """툴바 생성"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 버튼들
        ttk.Button(toolbar_frame, text="➕ 새 항목", command=self.add_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="✏️ 수정", command=self.edit_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="🗑️ 삭제", command=self.delete_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="💰 판매", command=self.sell_by_barcode).pack(side=tk.LEFT, padx=(0, 5))
        
        # 구분선
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(toolbar_frame, text="📊 통계", command=self.show_statistics).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="🔄 새로고침", command=self.refresh_data).pack(side=tk.LEFT, padx=(0, 5))
        
        # 구분선
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(toolbar_frame, text="📥 CSV 가져오기", command=self.import_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="📤 CSV 내보내기", command=self.export_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="📄 HTML 보고서", command=self.export_html).pack(side=tk.LEFT, padx=(0, 5))
    
    def create_search_panel(self, parent):
        """검색 패널 생성"""
        search_frame = ttk.LabelFrame(parent, text="검색 조건", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 첫 번째 행
        row1 = ttk.Frame(search_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row1, text="키워드:").pack(side=tk.LEFT, padx=(0, 5))
        self.keyword_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.keyword_var, width=20).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1, text="위치:").pack(side=tk.LEFT, padx=(0, 5))
        self.location_var = tk.StringVar()
        location_combo = ttk.Combobox(row1, textvariable=self.location_var, width=15)
        location_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1, text="구매처:").pack(side=tk.LEFT, padx=(0, 5))
        self.vendor_var = tk.StringVar()
        vendor_combo = ttk.Combobox(row1, textvariable=self.vendor_var, width=15)
        vendor_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # 두 번째 행
        row2 = ttk.Frame(search_frame)
        row2.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row2, text="모델명:").pack(side=tk.LEFT, padx=(0, 5))
        self.model_name_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.model_name_var, width=20).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row2, text="제품명:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.name_var, width=20).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row2, text="사이즈:").pack(side=tk.LEFT, padx=(0, 5))
        self.size_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.size_var, width=10).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row2, text="바코드:").pack(side=tk.LEFT, padx=(0, 5))
        self.barcode_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.barcode_var, width=15).pack(side=tk.LEFT, padx=(0, 20))
        
        # 세 번째 행 (날짜 범위)
        row3 = ttk.Frame(search_frame)
        row3.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(row3, text="구매일:").pack(side=tk.LEFT, padx=(0, 5))
        self.purchase_date_from_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.purchase_date_from_var, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(row3, text="~").pack(side=tk.LEFT, padx=(0, 5))
        self.purchase_date_to_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.purchase_date_to_var, width=12).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row3, text="판매일:").pack(side=tk.LEFT, padx=(0, 5))
        self.sale_date_from_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.sale_date_from_var, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(row3, text="~").pack(side=tk.LEFT, padx=(0, 5))
        self.sale_date_to_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.sale_date_to_var, width=12).pack(side=tk.LEFT, padx=(0, 20))
        
        # 네 번째 행 (가격 범위 및 버튼)
        row4 = ttk.Frame(search_frame)
        row4.pack(fill=tk.X)
        
        ttk.Label(row4, text="가격:").pack(side=tk.LEFT, padx=(0, 5))
        self.price_min_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.price_min_var, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(row4, text="~").pack(side=tk.LEFT, padx=(0, 5))
        self.price_max_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.price_max_var, width=12).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(row4, text="검색", command=self.search_items).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(row4, text="초기화", command=self.clear_search).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(row4, text="새로고침", command=self.refresh_data).pack(side=tk.LEFT)
        
        # 콤보박스 데이터 로드
        self.load_combo_data()
    
    def create_list_panel(self, parent):
        """목록 패널 생성"""
        list_frame = ttk.LabelFrame(parent, text="재고 목록", padding=5)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 트리뷰 생성
        columns = ("ID", "위치", "구매일", "판매일", "모델명", "이름", "사이즈", "바코드", "구매처", "가격", "상태")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 컬럼 설정
        column_widths = [50, 80, 100, 100, 120, 150, 60, 120, 100, 100, 60]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, minwidth=50)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 배치
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 이벤트 바인딩
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tree.bind("<Double-1>", self.edit_item)
    
    def create_detail_panel(self, parent):
        """상세 정보 패널 생성"""
        detail_frame = ttk.LabelFrame(parent, text="상세 정보", padding=5)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 상세 정보 텍스트 위젯
        self.detail_text = tk.Text(detail_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_status_bar(self, parent):
        """상태바 생성"""
        self.status_var = tk.StringVar()
        self.status_var.set("준비")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def load_combo_data(self):
        """콤보박스 데이터 로드"""
        try:
            # 백그라운드에서 실행
            def load_data():
                try:
                    with db_manager.get_session_context() as session:
                        repository = InventoryRepository(session)
                        locations = repository.get_locations()
                        vendors = repository.get_vendors()
                    
                    # UI 스레드에서 업데이트
                    self.root.after(0, lambda: self.update_combo_data(locations, vendors))
                except Exception as e:
                    logger.error(f"콤보박스 데이터 로드 실패: {e}")
            
            threading.Thread(target=load_data, daemon=True).start()
            
        except Exception as e:
            logger.error(f"콤보박스 데이터 로드 실패: {e}")
    
    def update_combo_data(self, locations: List[str], vendors: List[str]):
        """콤보박스 데이터 업데이트"""
        try:
            # 위치 콤보박스 업데이트
            location_combo = None
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Frame):
                                    for great_grandchild in grandchild.winfo_children():
                                        if isinstance(great_grandchild, ttk.Combobox):
                                            if great_grandchild.cget('textvariable') == str(self.location_var):
                                                location_combo = great_grandchild
                                                break
            
            if location_combo:
                location_combo['values'] = locations
            
            # 구매처 콤보박스 업데이트
            vendor_combo = None
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ttk.Frame):
                                    for great_grandchild in grandchild.winfo_children():
                                        if isinstance(great_grandchild, ttk.Combobox):
                                            if great_grandchild.cget('textvariable') == str(self.vendor_var):
                                                vendor_combo = great_grandchild
                                                break
            
            if vendor_combo:
                vendor_combo['values'] = vendors
                
        except Exception as e:
            logger.error(f"콤보박스 업데이트 실패: {e}")
    
    def search_items(self):
        """항목 검색"""
        try:
            # 검색 조건 구성
            search_query = SearchQuery(
                keyword=self.keyword_var.get() or None,
                location=self.location_var.get() or None,
                model_name=self.model_name_var.get() or None,
                name=self.name_var.get() or None,
                vendor=self.vendor_var.get() or None,
                size=self.size_var.get() or None,
                barcode=self.barcode_var.get() or None,
                purchase_date_from=self._parse_date(self.purchase_date_from_var.get()) if self.purchase_date_from_var.get() else None,
                purchase_date_to=self._parse_date(self.purchase_date_to_var.get()) if self.purchase_date_to_var.get() else None,
                sale_date_from=self._parse_date(self.sale_date_from_var.get()) if self.sale_date_from_var.get() else None,
                sale_date_to=self._parse_date(self.sale_date_to_var.get()) if self.sale_date_to_var.get() else None,
                price_min=Decimal(self.price_min_var.get()) if self.price_min_var.get() else None,
                price_max=Decimal(self.price_max_var.get()) if self.price_max_var.get() else None,
                sort_by=self.sort_column,
                sort_desc=self.sort_desc,
                limit=1000
            )
            
            # 백그라운드에서 검색 실행
            def search():
                try:
                    self.status_var.set("검색 중...")
                    with db_manager.get_session_context() as session:
                        repository = InventoryRepository(session)
                        result = repository.search(search_query)
                    self.root.after(0, lambda: self.update_search_results(result))
                except Exception as e:
                    logger.error(f"검색 실패: {e}")
                    self.root.after(0, lambda: self.status_var.set(f"검색 실패: {e}"))
            
            threading.Thread(target=search, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("오류", f"검색 실패: {e}")
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """날짜 문자열 파싱"""
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y/%m/%d').date()
            except ValueError:
                return None
    
    def update_search_results(self, result):
        """검색 결과 업데이트"""
        try:
            # 컬럼 헤더 업데이트 (정렬 방향 표시)
            self.update_column_headers()
            
            # 트리뷰 초기화
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 결과 추가
            for item in result.items:
                status = "판매됨" if item.sale_date else "재고"
                self.tree.insert("", tk.END, values=(
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
                ))
            
            self.status_var.set(f"검색 완료: {len(result.items)}개 항목 (전체 {result.total_count}개)")
            
        except Exception as e:
            logger.error(f"검색 결과 업데이트 실패: {e}")
            self.status_var.set(f"검색 결과 업데이트 실패: {e}")
    
    def clear_search(self):
        """검색 조건 초기화"""
        self.keyword_var.set("")
        self.location_var.set("")
        self.model_name_var.set("")
        self.name_var.set("")
        self.vendor_var.set("")
        self.size_var.set("")
        self.barcode_var.set("")
        self.purchase_date_from_var.set("")
        self.purchase_date_to_var.set("")
        self.sale_date_from_var.set("")
        self.sale_date_to_var.set("")
        self.price_min_var.set("")
        self.price_max_var.set("")
        self.refresh_data()
    
    def sort_by_column(self, column):
        """컬럼별 정렬"""
        # 컬럼명을 데이터베이스 필드명으로 매핑
        column_mapping = {
            "ID": "id",
            "위치": "location", 
            "구매일": "purchase_date",
            "판매일": "sale_date",
            "모델명": "model_name",
            "이름": "name",
            "사이즈": "size",
            "바코드": "barcode",
            "구매처": "vendor",
            "가격": "price",
            "상태": "created_at"  # 상태는 정렬 기준이 없으므로 생성일로 대체
        }
        
        db_column = column_mapping.get(column, "created_at")
        
        # 같은 컬럼을 클릭하면 정렬 방향 토글
        if self.sort_column == db_column:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_column = db_column
            self.sort_desc = True  # 새 컬럼은 기본적으로 내림차순
        
        # 정렬 방향 표시를 위해 컬럼 헤더 텍스트 업데이트
        self.update_column_headers()
        
        # 데이터 새로고침
        self.refresh_data()
    
    def update_column_headers(self):
        """컬럼 헤더에 정렬 방향 표시"""
        columns = ("ID", "위치", "구매일", "판매일", "모델명", "이름", "사이즈", "구매처", "가격", "상태")
        column_mapping = {
            "ID": "id",
            "위치": "location", 
            "구매일": "purchase_date",
            "판매일": "sale_date",
            "모델명": "model_name",
            "이름": "name",
            "사이즈": "size",
            "구매처": "vendor",
            "가격": "price",
            "상태": "created_at"
        }
        
        for col in columns:
            db_column = column_mapping.get(col, "created_at")
            if db_column == self.sort_column:
                # 현재 정렬 중인 컬럼에 화살표 표시
                arrow = " ↓" if self.sort_desc else " ↑"
                self.tree.heading(col, text=col + arrow)
            else:
                self.tree.heading(col, text=col)
    
    def refresh_data(self):
        """데이터 새로고침"""
        try:
            self.status_var.set("데이터 로딩 중...")
            
            # 백그라운드에서 실행
            def load_data():
                try:
                    with db_manager.get_session_context() as session:
                        repository = InventoryRepository(session)
                        result = repository.search(SearchQuery(
                            limit=1000,
                            sort_by=self.sort_column,
                            sort_desc=self.sort_desc
                        ))
                    self.root.after(0, lambda: self.update_search_results(result))
                except Exception as e:
                    logger.error(f"데이터 새로고침 실패: {e}")
                    error_msg = str(e)
                    self.root.after(0, lambda: self.status_var.set(f"데이터 로딩 실패: {error_msg}"))
            
            threading.Thread(target=load_data, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("오류", f"데이터 새로고침 실패: {e}")
    
    def on_item_select(self, event):
        """항목 선택 이벤트 처리"""
        try:
            selection = self.tree.selection()
            if not selection:
                self.selected_item = None
                self.detail_text.config(state=tk.NORMAL)
                self.detail_text.delete(1.0, tk.END)
                self.detail_text.config(state=tk.DISABLED)
                return
            
            item = self.tree.item(selection[0])
            item_id = item['values'][0]  # UUID는 문자열이므로 int() 변환 제거
            
            # 데이터베이스에서 상세 정보 조회
            def load_detail():
                try:
                    with db_manager.get_session_context() as session:
                        repository = InventoryRepository(session)
                        detail_item = repository.get_by_id(item_id)
                        if detail_item:
                            # 세션 컨텍스트 내에서 딕셔너리로 변환
                            item_data = {
                                'id': detail_item.id,
                                'location': detail_item.location,
                                'purchase_date': detail_item.purchase_date,
                                'sale_date': detail_item.sale_date,
                                'model_name': detail_item.model_name,
                                'name': detail_item.name,
                                'size': detail_item.size,
                                'barcode': detail_item.barcode,
                                'vendor': detail_item.vendor,
                                'price': detail_item.price,
                                'notes': detail_item.notes,
                                'created_at': detail_item.created_at,
                                'updated_at': detail_item.updated_at
                            }
                            self.root.after(0, lambda: self.update_detail_info_from_dict(item_data))
                except Exception as e:
                    logger.error(f"상세 정보 조회 실패: {e}")
            
            threading.Thread(target=load_detail, daemon=True).start()
            
        except Exception as e:
            logger.error(f"항목 선택 처리 실패: {e}")
    
    def update_detail_info_from_dict(self, item_data):
        """딕셔너리 데이터로부터 상세 정보 업데이트"""
        try:
            # 딕셔너리를 InventoryItemResponse 객체로 변환하여 저장
            from app.schemas import InventoryItemResponse
            self.selected_item = InventoryItemResponse(**item_data)
            
            # 딕셔너리 데이터를 사용하여 상세 정보 텍스트 생성
            detail_text = f"""
상세 정보 (ID: {item_data['id']})
{'=' * 50}

위치: {item_data['location']}
구매일: {item_data['purchase_date']}
판매일: {item_data['sale_date'] or '미판매'}
모델명: {item_data['model_name']}
이름: {item_data['name']}
사이즈: {item_data['size'] or '미지정'}
바코드: {item_data['barcode'] or '미지정'}
구매처: {item_data['vendor']}
가격: ₩{item_data['price']:,.0f}
상태: {'판매됨' if item_data['sale_date'] else '재고'}

메모:
{item_data['notes'] or '없음'}

생성일시: {item_data['created_at']}
수정일시: {item_data['updated_at']}
"""
            
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, detail_text)
            self.detail_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"상세 정보 업데이트 실패: {e}")
            # 에러 발생 시 기본 메시지 표시
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, "상세 정보를 불러올 수 없습니다.")
            self.detail_text.config(state=tk.DISABLED)
    
    def update_detail_info(self, item):
        """상세 정보 업데이트"""
        try:
            # SQLAlchemy 객체의 속성에 안전하게 접근하여 딕셔너리로 변환
            item_data = {}
            
            # 각 속성을 개별적으로 안전하게 접근
            try:
                item_data['id'] = item.id
            except:
                item_data['id'] = None
                
            try:
                item_data['location'] = item.location
            except:
                item_data['location'] = None
                
            try:
                item_data['purchase_date'] = item.purchase_date
            except:
                item_data['purchase_date'] = None
                
            try:
                item_data['sale_date'] = item.sale_date
            except:
                item_data['sale_date'] = None
                
            try:
                item_data['model_name'] = item.model_name
            except:
                item_data['model_name'] = None
                
            try:
                item_data['name'] = item.name
            except:
                item_data['name'] = None
                
            try:
                item_data['size'] = item.size
            except:
                item_data['size'] = None
                
            try:
                item_data['vendor'] = item.vendor
            except:
                item_data['vendor'] = None
                
            try:
                item_data['price'] = item.price
            except:
                item_data['price'] = None
                
            try:
                item_data['notes'] = item.notes
            except:
                item_data['notes'] = None
                
            try:
                item_data['created_at'] = item.created_at
            except:
                item_data['created_at'] = None
                
            try:
                item_data['updated_at'] = item.updated_at
            except:
                item_data['updated_at'] = None
            
            # 딕셔너리를 InventoryItemResponse 객체로 변환하여 저장
            from app.schemas import InventoryItemResponse
            self.selected_item = InventoryItemResponse(**item_data)
            
            # 딕셔너리 데이터를 사용하여 상세 정보 텍스트 생성
            detail_text = f"""
상세 정보 (ID: {item_data['id']})
{'=' * 50}

위치: {item_data['location']}
구매일: {item_data['purchase_date']}
판매일: {item_data['sale_date'] or '미판매'}
모델명: {item_data['model_name']}
이름: {item_data['name']}
사이즈: {item_data['size'] or '미지정'}
바코드: {item_data['barcode'] or '미지정'}
구매처: {item_data['vendor']}
가격: ₩{item_data['price']:,.0f}
상태: {'판매됨' if item_data['sale_date'] else '재고'}

메모:
{item_data['notes'] or '없음'}

생성일시: {item_data['created_at']}
수정일시: {item_data['updated_at']}
"""
            
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, detail_text)
            self.detail_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"상세 정보 업데이트 실패: {e}")
            # 에러 발생 시 기본 메시지 표시
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, "상세 정보를 불러올 수 없습니다.")
            self.detail_text.config(state=tk.DISABLED)
    
    def add_item(self):
        """새 항목 추가"""
        dialog = ItemDialog(self.root, "새 항목 추가")
        if dialog.result:
            try:
                self.status_var.set("항목 추가 중...")
                
                def add_item():
                    try:
                        with db_manager.get_session_context() as session:
                            repository = InventoryRepository(session)
                            repository.create_with_barcode_update(dialog.result)
                        self.root.after(0, lambda: self.refresh_data())
                        self.root.after(0, lambda: self.status_var.set("항목 추가 완료"))
                    except Exception as e:
                        logger.error(f"항목 추가 실패: {e}")
                        self.root.after(0, lambda: messagebox.showerror("오류", f"항목 추가 실패: {e}"))
                        self.root.after(0, lambda: self.status_var.set("항목 추가 실패"))
                
                threading.Thread(target=add_item, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("오류", f"항목 추가 실패: {e}")
    
    def edit_item(self, event=None):
        """항목 수정"""
        if not self.selected_item:
            messagebox.showwarning("경고", "수정할 항목을 선택하세요.")
            return
        
        try:
            dialog = ItemDialog(self.root, "항목 수정", self.selected_item)
            if dialog.result:
                self.status_var.set("항목 수정 중...")
                
                def update_item():
                    try:
                        with db_manager.get_session_context() as session:
                            repository = InventoryRepository(session)
                            repository.update(self.selected_item.id, dialog.result)
                        self.root.after(0, lambda: self.refresh_data())
                        self.root.after(0, lambda: self.status_var.set("항목 수정 완료"))
                    except Exception as e:
                        logger.error(f"항목 수정 실패: {e}")
                        self.root.after(0, lambda: messagebox.showerror("오류", f"항목 수정 실패: {e}"))
                        self.root.after(0, lambda: self.status_var.set("항목 수정 실패"))
                
                threading.Thread(target=update_item, daemon=True).start()
                
        except Exception as e:
            logger.error(f"항목 수정 다이얼로그 실패: {e}")
            messagebox.showerror("오류", f"항목 수정 실패: {e}")
    
    def delete_item(self):
        """항목 삭제"""
        if not self.selected_item:
            messagebox.showwarning("경고", "삭제할 항목을 선택하세요.")
            return
        
        if messagebox.askyesno("확인", f"'{self.selected_item.name}' 항목을 삭제하시겠습니까?"):
            try:
                self.status_var.set("항목 삭제 중...")
                
                def delete_item():
                    try:
                        with db_manager.get_session_context() as session:
                            repository = InventoryRepository(session)
                            repository.delete(self.selected_item.id)
                        self.root.after(0, lambda: self.refresh_data())
                        self.root.after(0, lambda: self.status_var.set("항목 삭제 완료"))
                    except Exception as e:
                        logger.error(f"항목 삭제 실패: {e}")
                        self.root.after(0, lambda: messagebox.showerror("오류", f"항목 삭제 실패: {e}"))
                        self.root.after(0, lambda: self.status_var.set("항목 삭제 실패"))
                
                threading.Thread(target=delete_item, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("오류", f"항목 삭제 실패: {e}")
    
    def import_csv(self):
        """CSV 가져오기"""
        file_path = filedialog.askopenfilename(
            title="CSV 파일 선택",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.status_var.set("CSV 가져오기 중...")
                
                def import_csv():
                    try:
                        result = self.import_service.import_from_csv(file_path, True)
                        self.root.after(0, lambda: self.show_import_result(result))
                        self.root.after(0, lambda: self.refresh_data())
                    except Exception as e:
                        logger.error(f"CSV 가져오기 실패: {e}")
                        self.root.after(0, lambda: messagebox.showerror("오류", f"CSV 가져오기 실패: {e}"))
                        self.root.after(0, lambda: self.status_var.set("CSV 가져오기 실패"))
                
                threading.Thread(target=import_csv, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("오류", f"CSV 가져오기 실패: {e}")
    
    def show_import_result(self, result):
        """가져오기 결과 표시"""
        message = f"가져오기 완료\n성공: {result.success_count}개\n실패: {result.error_count}개"
        if result.error_count > 0:
            message += f"\n오류 파일: {result.error_file_path}"
        
        messagebox.showinfo("가져오기 결과", message)
        self.status_var.set(f"CSV 가져오기 완료: 성공 {result.success_count}개, 실패 {result.error_count}개")
    
    def export_csv(self):
        """CSV 내보내기"""
        file_path = filedialog.asksaveasfilename(
            title="CSV 파일 저장",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.status_var.set("CSV 내보내기 중...")
                
                def export_csv():
                    try:
                        self.export_service.export_to_csv(file_path)
                        self.root.after(0, lambda: messagebox.showinfo("완료", f"CSV 내보내기 완료: {file_path}"))
                        self.root.after(0, lambda: self.status_var.set("CSV 내보내기 완료"))
                    except Exception as e:
                        logger.error(f"CSV 내보내기 실패: {e}")
                        self.root.after(0, lambda: messagebox.showerror("오류", f"CSV 내보내기 실패: {e}"))
                        self.root.after(0, lambda: self.status_var.set("CSV 내보내기 실패"))
                
                threading.Thread(target=export_csv, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("오류", f"CSV 내보내기 실패: {e}")
    
    def export_html(self):
        """HTML 내보내기"""
        file_path = filedialog.asksaveasfilename(
            title="HTML 파일 저장",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.status_var.set("HTML 내보내기 중...")
                
                def export_html():
                    try:
                        self.export_service.export_to_html(file_path)
                        self.root.after(0, lambda: messagebox.showinfo("완료", f"HTML 내보내기 완료: {file_path}"))
                        self.root.after(0, lambda: self.status_var.set("HTML 내보내기 완료"))
                    except Exception as e:
                        logger.error(f"HTML 내보내기 실패: {e}")
                        self.root.after(0, lambda: messagebox.showerror("오류", f"HTML 내보내기 실패: {e}"))
                        self.root.after(0, lambda: self.status_var.set("HTML 내보내기 실패"))
                
                threading.Thread(target=export_html, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("오류", f"HTML 내보내기 실패: {e}")
    
    def show_statistics(self):
        """통계 보기"""
        try:
            self.status_var.set("통계 조회 중...")
            
            def load_stats():
                try:
                    with db_manager.get_session_context() as session:
                        repository = InventoryRepository(session)
                        stats = repository.get_statistics()
                        vendors = repository.get_vendors()
                        locations = repository.get_locations()
                    
                    self.root.after(0, lambda: self.show_stats_dialog(stats, vendors, locations))
                except Exception as e:
                    logger.error(f"통계 조회 실패: {e}")
                    self.root.after(0, lambda: messagebox.showerror("오류", f"통계 조회 실패: {e}"))
                    self.root.after(0, lambda: self.status_var.set("통계 조회 실패"))
            
            threading.Thread(target=load_stats, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("오류", f"통계 조회 실패: {e}")
    
    def show_stats_dialog(self, stats, vendors, locations):
        """통계 다이얼로그 표시"""
        dialog = StatisticsDialog(self.root, stats, vendors, locations)
        self.status_var.set("통계 조회 완료")
    
    def sell_by_barcode(self):
        """바코드로 판매"""
        dialog = SellDialog(self.root)
        if dialog.result:
            try:
                self.status_var.set("판매 처리 중...")
                
                def sell_item():
                    try:
                        with db_manager.get_session_context() as session:
                            repository = InventoryRepository(session)
                            success = repository.sell_item(dialog.result['item_id'], dialog.result['sale_date'])
                            
                        if success:
                            self.root.after(0, lambda: self.refresh_data())
                            self.root.after(0, lambda: self.status_var.set("판매 처리 완료"))
                        else:
                            self.root.after(0, lambda: messagebox.showerror("오류", "판매 처리에 실패했습니다."))
                            self.root.after(0, lambda: self.status_var.set("판매 처리 실패"))
                            
                    except Exception as e:
                        logger.error(f"판매 처리 실패: {e}")
                        self.root.after(0, lambda: messagebox.showerror("오류", f"판매 처리 실패: {e}"))
                        self.root.after(0, lambda: self.status_var.set("판매 처리 실패"))
                
                threading.Thread(target=sell_item, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("오류", f"판매 처리 실패: {e}")
    
    def on_closing(self):
        """애플리케이션 종료"""
        try:
            db_manager.close()
            self.root.destroy()
        except Exception as e:
            logger.error(f"애플리케이션 종료 실패: {e}")
            self.root.destroy()
    
    def run(self):
        """애플리케이션 실행"""
        self.root.mainloop()


class ItemDialog:
    """항목 추가/수정 다이얼로그"""
    
    def __init__(self, parent, title, item=None):
        self.result = None
        self.item = item  # item을 인스턴스 변수로 저장
        
        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 중앙에 배치
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # 폼 생성
        self.create_form(item)
        
        # 다이얼로그가 닫힐 때까지 대기
        self.dialog.wait_window()
    
    def create_form(self, item):
        """폼 생성"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 필드들 (config.py의 설정 사용)
        all_fields = [
            ("location", "위치"),
            ("purchase_date", "구매일"),
            ("sale_date", "판매일"),
            ("model_name", "모델명"),
            ("name", "제품명"),
            ("size", "사이즈"),
            ("barcode", "바코드"),
            ("vendor", "구매처"),
            ("price", "가격"),
            ("notes", "메모")
        ]
        
        # config.py의 required_fields 설정을 사용하여 필수/선택 필드 결정
        fields = []
        for field, label in all_fields:
            required = field in settings.required_fields
            fields.append((field, label, required))
        
        self.vars = {}
        self.barcode_entry = None  # 바코드 엔트리 위젯 저장용
        
        for i, (field, label, required) in enumerate(fields):
            ttk.Label(main_frame, text=f"{label}{'*' if required else ''}:").grid(
                row=i, column=0, sticky=tk.W, pady=5
            )
            
            if field == "notes":
                # 메모는 텍스트 위젯
                text_widget = tk.Text(main_frame, height=4, width=40)
                text_widget.grid(row=i, column=1, sticky=tk.W+tk.E, pady=5)
                self.vars[field] = text_widget
            else:
                # 일반 입력 필드
                var = tk.StringVar()
                entry = ttk.Entry(main_frame, textvariable=var, width=40)
                entry.grid(row=i, column=1, sticky=tk.W+tk.E, pady=5)
                self.vars[field] = var
                
                # 바코드 필드에 이벤트 리스너 추가 및 엔트리 위젯 저장
                if field == "barcode":
                    var.trace_add('write', self.on_barcode_changed)
                    self.barcode_entry = entry
        
        # 기존 데이터 로드 또는 기본값 설정
        if item:
            # 수정 모드: 기존 데이터 로드
            self.vars["location"].set(item.location or '')
            self.vars["purchase_date"].set(item.purchase_date.strftime('%Y-%m-%d') if item.purchase_date else '')
            self.vars["sale_date"].set(item.sale_date.strftime('%Y-%m-%d') if item.sale_date else '')
            self.vars["model_name"].set(item.model_name or '')
            self.vars["name"].set(item.name or '')
            self.vars["size"].set(item.size or '')
            self.vars["barcode"].set(item.barcode or '')
            self.vars["vendor"].set(item.vendor or '')
            self.vars["price"].set(str(item.price) if item.price else '')
            self.vars["notes"].insert(1.0, item.notes or '')
        else:
            # 추가 모드: 기본값 설정
            self.vars["location"].set(settings.default_location)
            self.vars["vendor"].set(settings.default_vendor)
            # 오늘 날짜를 기본 구매일로 설정
            self.vars["purchase_date"].set(datetime.now().strftime('%Y-%m-%d'))
        
        # 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="저장", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # 새 항목 추가 모드일 때 바코드 필드에 포커스 설정
        if not item and self.barcode_entry:
            self.dialog.after(100, lambda: self.barcode_entry.focus_set())
    
    def save(self):
        """저장"""
        try:
            # 데이터 수집
            data = {}
            for field, widget in self.vars.items():
                if field == "notes":
                    value = widget.get(1.0, tk.END).strip()
                else:
                    value = widget.get().strip()
                
                # config.py의 required_fields 설정을 사용하여 필수 필드 검증
                if not value and field in settings.required_fields:
                    field_labels = {
                        "location": "위치",
                        "purchase_date": "구매일", 
                        "model_name": "모델명",
                        "name": "제품명",
                        "vendor": "구매처",
                        "price": "가격"
                    }
                    field_label = field_labels.get(field, field)
                    messagebox.showerror("오류", f"{field_label}은(는) 필수 입력 항목입니다.")
                    return
                
                data[field] = value if value else None
            
            # 날짜 파싱
            if data["purchase_date"]:
                data["purchase_date"] = datetime.strptime(data["purchase_date"], '%Y-%m-%d').date()
            if data["sale_date"]:
                data["sale_date"] = datetime.strptime(data["sale_date"], '%Y-%m-%d').date()
            
            # 가격 파싱
            if data["price"]:
                data["price"] = Decimal(data["price"])
            
            # 스키마 생성
            if self.item:
                self.result = InventoryItemUpdate(**data)
            else:
                self.result = InventoryItemCreate(**data)
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("오류", f"데이터 저장 실패: {e}")
    
    def on_barcode_changed(self, *args):
        """바코드 변경 시 기존 바코드 정보 자동 채우기"""
        try:
            barcode = self.vars["barcode"].get().strip()
            if not barcode or len(barcode) < 5:  # 최소 5자리 이상일 때만 검색
                return
            
            # 데이터베이스에서 바코드 정보 조회
            from app.db import db_manager
            from app.repository import InventoryRepository
            
            with db_manager.get_session_context() as session:
                repository = InventoryRepository(session)
                
                # 가장 최근의 재고 항목 조회 (사이즈, 가격 포함)
                latest_item = repository.get_latest_inventory_by_barcode(barcode)
                
                if latest_item:
                    # 기존 재고 항목이 있으면 모든 정보 자동 채우기
                    # 현재 필드가 비어있을 때만 채우기 (기존 데이터 보호)
                    if not self.vars["model_name"].get().strip():
                        self.vars["model_name"].set(latest_item.model_name)
                    if not self.vars["name"].get().strip():
                        self.vars["name"].set(latest_item.name)
                    if not self.vars["size"].get().strip():
                        self.vars["size"].set(latest_item.size or '')
                    if not self.vars["price"].get().strip():
                        self.vars["price"].set(str(latest_item.price) if latest_item.price else '')
                    if not self.vars["vendor"].get().strip():
                        self.vars["vendor"].set(latest_item.vendor)
                else:
                    # 바코드가 저장되어 있지 않으면 사용자에게 알림
                    # 기존 필드들을 비워두고 새로 입력하도록 함
                    if not self.vars["model_name"].get().strip():
                        self.vars["model_name"].set("")
                    if not self.vars["name"].get().strip():
                        self.vars["name"].set("")
                    if not self.vars["size"].get().strip():
                        self.vars["size"].set("")
                    if not self.vars["price"].get().strip():
                        self.vars["price"].set("")
                    if not self.vars["vendor"].get().strip():
                        self.vars["vendor"].set("")
                    
                    # 상태 표시 (선택사항)
                    print(f"새로운 바코드: {barcode} - 수동으로 정보를 입력해주세요.")
                        
        except Exception as e:
            # 바코드 조회 실패는 무시 (사용자 입력 중일 수 있음)
            pass
    
    def cancel(self):
        """취소"""
        self.dialog.destroy()


class SellDialog:
    """판매 다이얼로그"""
    
    def __init__(self, parent):
        self.result = None
        
        # 다이얼로그 창 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("바코드로 판매")
        self.dialog.geometry("600x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 중앙에 배치
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # 폼 생성
        self.create_form()
        
        # 다이얼로그가 닫힐 때까지 대기
        self.dialog.wait_window()
    
    def create_form(self):
        """폼 생성"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 바코드 입력
        ttk.Label(main_frame, text="바코드:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.barcode_var = tk.StringVar()
        self.barcode_entry = ttk.Entry(main_frame, textvariable=self.barcode_var, width=40)
        self.barcode_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 바코드 변경 이벤트
        self.barcode_var.trace_add('write', self.on_barcode_changed)
        
        # 검색 버튼
        ttk.Button(main_frame, text="검색", command=self.search_items).grid(row=0, column=2, padx=5)
        
        # 결과 목록
        ttk.Label(main_frame, text="재고 목록:").grid(row=1, column=0, sticky=tk.W, pady=(20, 5))
        
        # 트리뷰 생성
        columns = ("ID", "위치", "구매일", "모델명", "이름", "사이즈", "가격", "구매처")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=8)
        
        # 컬럼 설정
        column_widths = [50, 80, 100, 120, 150, 60, 100, 100]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=50)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 배치
        self.tree.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        scrollbar.grid(row=2, column=3, sticky=tk.N+tk.S)
        
        # 이벤트 바인딩
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        
        # 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.sell_button = ttk.Button(button_frame, text="판매", command=self.sell_item, state=tk.DISABLED)
        self.sell_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # 바코드 필드에 포커스
        self.dialog.after(100, lambda: self.barcode_entry.focus_set())
    
    def on_barcode_changed(self, *args):
        """바코드 변경 시 자동 검색"""
        barcode = self.barcode_var.get().strip()
        if len(barcode) >= 5:  # 5자리 이상일 때만 자동 검색
            self.search_items()
    
    def search_items(self):
        """재고 항목 검색"""
        try:
            barcode = self.barcode_var.get().strip()
            if not barcode:
                return
            
            # 트리뷰 초기화
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 데이터베이스에서 검색
            from app.db import db_manager
            from app.repository import InventoryRepository
            
            with db_manager.get_session_context() as session:
                repository = InventoryRepository(session)
                items = repository.get_inventory_by_barcode(barcode)
                
                if not items:
                    messagebox.showinfo("알림", f"바코드 '{barcode}'에 해당하는 재고가 없습니다.")
                    return
                
                # 결과 추가
                for item in items:
                    self.tree.insert("", tk.END, values=(
                        item.id,
                        item.location,
                        item.purchase_date.strftime('%Y-%m-%d') if item.purchase_date else '',
                        item.model_name,
                        item.name,
                        item.size or '',
                        f"₩{item.price:,.0f}",
                        item.vendor
                    ))
                
        except Exception as e:
            messagebox.showerror("오류", f"검색 실패: {e}")
    
    def on_item_select(self, event):
        """항목 선택 이벤트"""
        selection = self.tree.selection()
        if selection:
            self.sell_button.config(state=tk.NORMAL)
        else:
            self.sell_button.config(state=tk.DISABLED)
    
    def sell_item(self):
        """항목 판매"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("경고", "판매할 항목을 선택하세요.")
                return
            
            item = self.tree.item(selection[0])
            item_id = item['values'][0]
            
            # 오늘 날짜로 판매 처리
            from datetime import date
            sale_date = date.today()
            
            self.result = {
                'item_id': item_id,
                'sale_date': sale_date
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("오류", f"판매 처리 실패: {e}")
    
    def cancel(self):
        """취소"""
        self.dialog.destroy()


class StatisticsDialog:
    """통계 다이얼로그"""
    
    def __init__(self, parent, stats, vendors, locations):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("재고 통계")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 중앙에 배치
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        # 통계 표시
        self.create_stats_display(stats, vendors, locations)
        
        # 닫기 버튼
        ttk.Button(self.dialog, text="닫기", command=self.dialog.destroy).pack(pady=10)
    
    def create_stats_display(self, stats, vendors, locations):
        """통계 표시"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 기본 통계
        stats_frame = ttk.LabelFrame(main_frame, text="기본 통계", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        stats_text = f"""
전체 항목: {stats['total_items']:,}개
재고 항목: {stats['in_stock_items']:,}개
판매된 항목: {stats['sold_items']:,}개
총 재고 가치: ₩{stats['total_value']:,.0f}
평균 가격: ₩{stats['average_price']:,.0f}
최고 가격: ₩{stats['max_price']:,.0f}
최저 가격: ₩{stats['min_price']:,.0f}
"""
        
        ttk.Label(stats_frame, text=stats_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # 구매처 목록
        vendors_frame = ttk.LabelFrame(main_frame, text="구매처 목록", padding=10)
        vendors_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        vendors_text = "\n".join([f"• {vendor}" for vendor in vendors])
        ttk.Label(vendors_frame, text=vendors_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # 위치 목록
        locations_frame = ttk.LabelFrame(main_frame, text="위치 목록", padding=10)
        locations_frame.pack(fill=tk.BOTH, expand=True)
        
        locations_text = "\n".join([f"• {location}" for location in locations])
        ttk.Label(locations_frame, text=locations_text, justify=tk.LEFT).pack(anchor=tk.W)


def main():
    """메인 함수"""
    try:
        app = InventoryApp()
        app.run()
    except Exception as e:
        logger.error(f"애플리케이션 실행 실패: {e}")
        messagebox.showerror("오류", f"애플리케이션 실행 실패: {e}")


if __name__ == "__main__":
    main()
