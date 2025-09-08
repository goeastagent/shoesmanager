"""
환경 설정 관리 모듈

pydantic-settings를 사용하여 환경 변수에서 설정을 로드하고 검증합니다.
"""

import logging
from typing import Optional, List

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # MySQL 데이터베이스 설정
    mysql_host: str = Field(default="localhost", description="MySQL 호스트")
    mysql_port: int = Field(default=3306, description="MySQL 포트")
    mysql_db: str = Field(default="inventory_management", description="MySQL 데이터베이스명")
    mysql_user: str = Field(default="root", description="MySQL 사용자명")
    mysql_password: str = Field(default="", description="MySQL 비밀번호")
    
    # 애플리케이션 설정
    log_level: str = Field(default="INFO", description="로그 레벨")
    database_type: str = Field(default="sqlite", description="데이터베이스 타입 (sqlite/mysql)")
    
    # 필수 입력 항목 설정
    required_fields: List[str] = Field(
        default=["location", "purchase_date", "model_name", "name", "vendor", "price"],
        description="재고 등록 시 필수 입력 항목"
    )
    
    # 기본값 설정
    default_location: str = Field(default="A-01", description="기본 보관 위치")
    default_vendor: str = Field(default="기본구매처", description="기본 구매처")
    
    # 데이터베이스 연결 풀 설정
    pool_size: int = Field(default=10, description="연결 풀 크기")
    max_overflow: int = Field(default=20, description="최대 오버플로우")
    pool_timeout: int = Field(default=30, description="연결 풀 타임아웃(초)")
    pool_recycle: int = Field(default=3600, description="연결 재활용 시간(초)")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """로그 레벨 검증"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper()
    
    @validator('mysql_port')
    def validate_mysql_port(cls, v):
        """MySQL 포트 검증"""
        if not 1 <= v <= 65535:
            raise ValueError('mysql_port must be between 1 and 65535')
        return v
    
    @property
    def database_url(self) -> str:
        """데이터베이스 연결 URL 생성"""
        if self.database_type.lower() == "mysql":
            return (
                f"mysql+mysqldb://{self.mysql_user}:{self.mysql_password}"
                f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
                f"?charset=utf8mb4"
            )
        else:
            # SQLite 사용 (기본값)
            return f"sqlite:///./inventory_management.db"
    
    @property
    def test_database_url(self) -> str:
        """테스트 데이터베이스 연결 URL 생성"""
        return f"sqlite:///./inventory_management_test.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()


def setup_logging() -> None:
    """로깅 설정"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
