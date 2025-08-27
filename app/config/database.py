"""
DB 연결 모듈 (SQLAlchemy + MariaDB/RDS)
- 커넥션 풀/헬스체크/재활용 설정으로 Too many connections 예방
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# === 환경변수로 민감정보 관리 (하드코딩 금지) ===
DB_HOST = os.getenv("DB_HOST", "database-1.c3asgoye8svw.ap-northeast-2.rds.amazonaws.com")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "ajin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "agin1234")
DB_NAME = os.getenv("DB_NAME", "AJIN_newDB")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"[DB] connecting to {DB_HOST}:{DB_PORT}/{DB_NAME}")

# === 엔진(프로세스 전역에 단 1개) ===
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # 기본 풀 사이즈
    max_overflow=20,       # 초과 허용 커넥션
    pool_timeout=30,       # 풀에서 커넥션 얻기 대기시간
    pool_recycle=1800,     # 30분마다 재활용(오래된 커넥션 정리)
    pool_pre_ping=True,    # 죽은 커넥션 감지/복구
    future=True,
)

Base = declarative_base()

# 세션팩토리 (autocommit/autoflush 비활성)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

def get_db():
    """FastAPI Depends에서 사용: 요청마다 세션 열고 반드시 닫기"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """초기 테이블 생성(필요할 때만)"""
    try:
        Base.metadata.create_all(bind=engine)
        print("[DB] table creation success")
    except Exception as e:
        print(f"[DB] table creation failed: {e}")

# (선택) FastAPI 애플리케이션 종료 시 커넥션 정리:
# app.add_event_handler("shutdown", lambda: engine.dispose())
