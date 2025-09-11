"""
환경 설정 모듈
.env 파일에서 환경변수를 로드하고 애플리케이션 설정을 관리합니다.
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# OpenAI API 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("경고: OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    print("테스트 모드로 실행됩니다.")

# 데이터베이스 설정
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "database-1.c3asgoye8svw.ap-northeast-2.rds.amazonaws.com"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "ajin"),  # 읽기 전용 계정
    "password": os.getenv("DB_PASSWORD", "agin1234"),
    "database": os.getenv("DB_NAME", "AJIN_newDB"),
    "charset": "utf8mb4"
}

# ChromaDB 설정
CHROMA_PATH = os.getenv("CHROMA_PATH", "./app/chroma_db")

# CORS 설정 - 모든 URL에서 요청 허용
ALLOWED_ORIGINS = ["*"]  # 모든 도메인에서 요청 허용

# 문서 인덱싱 설정
DOC_INDEX_WINDOW_DAYS = int(os.getenv("DOC_INDEX_WINDOW_DAYS", "180"))

# RAG 설정
RAG_TOP_K = 10
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

# RAG 임베딩 백엔드 설정
RAG_USE_OPENAI = os.getenv("RAG_USE_OPENAI", "false").lower() == "true"
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
LOCAL_EMBED_MODEL = os.getenv("LOCAL_EMBED_MODEL", "intfloat/multilingual-e5-large-instruct")

# 임베딩 배치 크기
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "128"))
EMBEDDING_MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES", "3"))

# 안전한 SQL 쿼리 화이트리스트 (실제 테이블 구조에 맞게 수정)
SAFE_SQL_QUERIES = {
    "production_today": """
        SELECT 
            근무일자 as date,
            자재번호 as item_code,
            자재명 as item_name,
            차종 as car_model,
            작업장 as work_station,
            가동시간 as operation_time,
            양품수량 as good_quantity,
            생산수량 as total_production,
            불량합계 as total_defects,
            ROUND((양품수량 / NULLIF(생산수량, 0)) * 100, 2) as quality_rate,
            ROUND(양품수량 / NULLIF(가동시간, 0) * 60, 2) as uph
        FROM 생산내역 
        WHERE 근무일자 = CURDATE()
        AND (%s IS NULL OR 자재번호 LIKE %s)
        ORDER BY 양품수량 DESC
    """,
    
    "production_monthly": """
        SELECT 
            근무일자 as date,
            자재번호 as item_code,
            자재명 as item_name,
            차종 as car_model,
            작업장 as work_station,
            가동시간 as operation_time,
            양품수량 as good_quantity,
            생산수량 as total_production,
            불량합계 as total_defects,
            ROUND((양품수량 / NULLIF(생산수량, 0)) * 100, 2) as quality_rate,
            ROUND(양품수량 / NULLIF(가동시간, 0) * 60, 2) as uph
        FROM 생산내역 
        WHERE 근무일자 >= %s AND 근무일자 <= %s
        AND (%s IS NULL OR 자재번호 LIKE %s)
        ORDER BY 근무일자 DESC, 양품수량 DESC
    """,
    
    "mold_shot_progress": """
        SELECT 
            금형번호 as mold_code,
            금형내역 as mold_name,
            누적_Shot_수 as current_shots,
            점검타발수 as max_shots,
            진행률 as progress_rate,
            CASE 
                WHEN 진행률 >= 80 THEN '80% 임박'
                ELSE '정상'
            END as status
        FROM 금형타발수관리
        WHERE (%s IS NULL OR 금형번호 = %s)
        ORDER BY 진행률 DESC
    """,
    
    "defect_analysis": """
        SELECT 
            근무일자 as date,
            작업장 as work_station,
            자재번호 as item_code,
            차종 as car_model,
            불량유형 as defect_type,
            RWK_수량 as rework_quantity,
            폐기_수량 as scrap_quantity,
            (RWK_수량 + 폐기_수량) as total_defects
        FROM 불량수량_및_유형
        WHERE 근무일자 >= %s AND 근무일자 <= %s
        AND (%s IS NULL OR 자재번호 LIKE %s)
        ORDER BY 근무일자 DESC, (RWK_수량 + 폐기_수량) DESC
    """,
    
    "downtime_analysis": """
        SELECT 
            근무일자 as date,
            플랜트 as plant,
            작업장 as work_station,
            자재번호 as item_code,
            차종 as car_model,
            비가동명 as downtime_reason,
            비가동_분 as downtime_minutes,
            대분류 as category,
            소분류 as subcategory
        FROM 비가동시간_및_현황
        WHERE 근무일자 >= %s AND 근무일자 <= %s
        AND (%s IS NULL OR 자재번호 LIKE %s)
        ORDER BY 근무일자 DESC, 비가동_분 DESC
    """
}
