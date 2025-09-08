"""
CSV/HTML 내보내기 서비스

데이터베이스에서 데이터를 조회하여 CSV 또는 HTML 형식으로 내보냅니다.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.schemas import SearchQuery, SearchResult
from app.repository import InventoryRepository

logger = logging.getLogger(__name__)


class ExportService:
    """내보내기 서비스 클래스"""
    
    def __init__(self, repository: InventoryRepository):
        """
        내보내기 서비스 초기화
        
        Args:
            repository: 재고 Repository 인스턴스
        """
        self.repository = repository
    
    def export_to_csv(
        self,
        file_path: str,
        search_query: Optional[SearchQuery] = None,
        include_headers: bool = True
    ) -> str:
        """
        CSV 형식으로 데이터 내보내기
        
        Args:
            file_path: 출력 파일 경로
            search_query: 검색 조건 (None이면 전체 데이터)
            include_headers: 헤더 포함 여부
            
        Returns:
            str: 생성된 파일 경로
        """
        try:
            # 검색 쿼리가 없으면 전체 데이터 조회
            if search_query is None:
                search_query = SearchQuery(limit=10000)  # 큰 제한으로 전체 데이터 조회
            
            # 데이터 조회
            result = self.repository.search(search_query)
            
            # 파일 경로 생성
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # CSV 파일 작성
            with open(output_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                
                # 헤더 작성
                if include_headers:
                    headers = [
                        'ID', '위치', '구매일', '판매일', '모델명', '이름',
                        '사이즈', '구매처', '가격', '메모', '생성일시', '수정일시'
                    ]
                    writer.writerow(headers)
                
                # 데이터 작성
                for item in result.items:
                    row = [
                        item.id,
                        item.location,
                        item.purchase_date.strftime('%Y-%m-%d') if item.purchase_date else '',
                        item.sale_date.strftime('%Y-%m-%d') if item.sale_date else '',
                        item.model_name,
                        item.name,
                        item.size or '',
                        item.vendor,
                        str(item.price),
                        item.notes or '',
                        item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '',
                        item.updated_at.strftime('%Y-%m-%d %H:%M:%S') if item.updated_at else ''
                    ]
                    writer.writerow(row)
            
            logger.info(f"CSV 내보내기 완료: {output_path} ({len(result.items)}개 항목)")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"CSV 내보내기 실패: {e}")
            raise
    
    def export_to_html(
        self,
        file_path: str,
        search_query: Optional[SearchQuery] = None,
        title: str = "재고 관리 보고서"
    ) -> str:
        """
        HTML 형식으로 데이터 내보내기
        
        Args:
            file_path: 출력 파일 경로
            search_query: 검색 조건 (None이면 전체 데이터)
            title: 보고서 제목
            
        Returns:
            str: 생성된 파일 경로
        """
        try:
            # 검색 쿼리가 없으면 전체 데이터 조회
            if search_query is None:
                search_query = SearchQuery(limit=10000)
            
            # 데이터 조회
            result = self.repository.search(search_query)
            
            # 파일 경로 생성
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # HTML 생성
            html_content = self._generate_html_content(result, title)
            
            # HTML 파일 작성
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
            
            logger.info(f"HTML 내보내기 완료: {output_path} ({len(result.items)}개 항목)")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"HTML 내보내기 실패: {e}")
            raise
    
    def _generate_html_content(self, result: SearchResult, title: str) -> str:
        """
        HTML 콘텐츠 생성
        
        Args:
            result: 검색 결과
            title: 보고서 제목
            
        Returns:
            str: HTML 콘텐츠
        """
        # 통계 정보 생성
        stats = self.repository.get_statistics()
        
        # HTML 템플릿
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #333;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-sold {{
            color: #dc3545;
            font-weight: bold;
        }}
        .status-stock {{
            color: #28a745;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>전체 항목</h3>
                <div class="value">{stats['total_items']:,}</div>
            </div>
            <div class="stat-card">
                <h3>재고 항목</h3>
                <div class="value">{stats['in_stock_items']:,}</div>
            </div>
            <div class="stat-card">
                <h3>판매된 항목</h3>
                <div class="value">{stats['sold_items']:,}</div>
            </div>
            <div class="stat-card">
                <h3>총 재고 가치</h3>
                <div class="value">₩{stats['total_value']:,.0f}</div>
            </div>
            <div class="stat-card">
                <h3>평균 가격</h3>
                <div class="value">₩{stats['average_price']:,.0f}</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>위치</th>
                    <th>구매일</th>
                    <th>판매일</th>
                    <th>모델명</th>
                    <th>이름</th>
                    <th>사이즈</th>
                    <th>구매처</th>
                    <th>가격</th>
                    <th>상태</th>
                    <th>메모</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # 데이터 행 추가
        for item in result.items:
            status = "판매됨" if item.sale_date else "재고"
            status_class = "status-sold" if item.sale_date else "status-stock"
            
            html_template += f"""
                <tr>
                    <td>{item.id}</td>
                    <td>{item.location}</td>
                    <td>{item.purchase_date.strftime('%Y-%m-%d') if item.purchase_date else ''}</td>
                    <td>{item.sale_date.strftime('%Y-%m-%d') if item.sale_date else ''}</td>
                    <td>{item.model_name}</td>
                    <td>{item.name}</td>
                    <td>{item.size or ''}</td>
                    <td>{item.vendor}</td>
                    <td>₩{item.price:,.0f}</td>
                    <td class="{status_class}">{status}</td>
                    <td>{item.notes or ''}</td>
                </tr>
"""
        
        # HTML 마무리
        html_template += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <p>보고서 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>총 {len(result.items)}개 항목 (전체 {result.total_count}개 중)</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_template
    
    def export_statistics_report(self, file_path: str) -> str:
        """
        통계 보고서 내보내기
        
        Args:
            file_path: 출력 파일 경로
            
        Returns:
            str: 생성된 파일 경로
        """
        try:
            stats = self.repository.get_statistics()
            vendors = self.repository.get_vendors()
            locations = self.repository.get_locations()
            
            # 파일 경로 생성
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # HTML 콘텐츠 생성
            html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>재고 통계 보고서</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #007bff;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .list {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
        }}
        .list-item {{
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>재고 통계 보고서</h1>
        
        <div class="section">
            <h2>기본 통계</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value">{stats['total_items']:,}</div>
                    <div class="stat-label">전체 항목</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{stats['in_stock_items']:,}</div>
                    <div class="stat-label">재고 항목</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{stats['sold_items']:,}</div>
                    <div class="stat-label">판매된 항목</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">₩{stats['total_value']:,.0f}</div>
                    <div class="stat-label">총 재고 가치</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">₩{stats['average_price']:,.0f}</div>
                    <div class="stat-label">평균 가격</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">₩{stats['max_price']:,.0f}</div>
                    <div class="stat-label">최고 가격</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">₩{stats['min_price']:,.0f}</div>
                    <div class="stat-label">최저 가격</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>구매처 목록</h2>
            <div class="list">
                {''.join([f'<div class="list-item">{vendor}</div>' for vendor in vendors])}
            </div>
        </div>
        
        <div class="section">
            <h2>위치 목록</h2>
            <div class="list">
                {''.join([f'<div class="list-item">{location}</div>' for location in locations])}
            </div>
        </div>
        
        <div class="footer">
            <p>보고서 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
            
            # HTML 파일 작성
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
            
            logger.info(f"통계 보고서 내보내기 완료: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"통계 보고서 내보내기 실패: {e}")
            raise
