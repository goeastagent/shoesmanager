"""
데이터베이스 연결 및 세션 관리 모듈

SQLAlchemy 엔진, 세션 팩토리, 헬스체크 기능을 제공합니다.
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """데이터베이스 연결 및 세션 관리 클래스"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        데이터베이스 매니저 초기화
        
        Args:
            database_url: 데이터베이스 연결 URL (기본값: settings.database_url)
        """
        self.database_url = database_url or settings.database_url
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """SQLAlchemy 엔진 초기화"""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_size=settings.pool_size,
                max_overflow=settings.max_overflow,
                pool_timeout=settings.pool_timeout,
                pool_recycle=settings.pool_recycle,
                echo=False,  # SQL 쿼리 로깅 (개발 시에만 True)
                future=True
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("데이터베이스 엔진이 성공적으로 초기화되었습니다.")
            
        except Exception as e:
            logger.error(f"데이터베이스 엔진 초기화 실패: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        새로운 데이터베이스 세션 생성
        
        Returns:
            Session: SQLAlchemy 세션 객체
            
        Raises:
            SQLAlchemyError: 세션 생성 실패 시
        """
        if not self.SessionLocal:
            raise SQLAlchemyError("데이터베이스 엔진이 초기화되지 않았습니다.")
        
        return self.SessionLocal()
    
    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """
        컨텍스트 매니저를 사용한 세션 관리
        
        Yields:
            Session: SQLAlchemy 세션 객체
            
        Example:
            with db_manager.get_session_context() as session:
                # 데이터베이스 작업 수행
                pass
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"데이터베이스 세션 오류: {e}")
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """
        데이터베이스 연결 상태 확인
        
        Returns:
            bool: 연결 상태 (True: 정상, False: 오류)
        """
        if not self.engine:
            logger.error("데이터베이스 엔진이 초기화되지 않았습니다.")
            return False
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                logger.info("데이터베이스 연결 상태: 정상")
                return True
                
        except Exception as e:
            logger.error(f"데이터베이스 연결 상태 확인 실패: {e}")
            return False
    
    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()
            logger.info("데이터베이스 연결이 종료되었습니다.")


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()


def get_db_session() -> Generator[Session, None, None]:
    """
    FastAPI 스타일의 의존성 주입을 위한 세션 생성기
    
    Yields:
        Session: SQLAlchemy 세션 객체
    """
    with db_manager.get_session_context() as session:
        yield session


def check_database_connection() -> bool:
    """
    데이터베이스 연결 상태 확인 (유틸리티 함수)
    
    Returns:
        bool: 연결 상태
    """
    return db_manager.health_check()
