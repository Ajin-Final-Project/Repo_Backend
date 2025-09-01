"""
간단한 FastAPI 애플리케이션 - Company 테이블 조회 전용

이 모듈은 FastAPI 애플리케이션의 메인 진입점입니다.
Company 테이블 조회 기능만을 제공하는 간단한 REST API 서버를 구성합니다.

주요 기능:
- FastAPI 애플리케이션 초기화 및 설정
- CORS 미들웨어 설정
- API 라우터 등록
- 기본 엔드포인트 제공 (루트, 헬스체크)
- uvicorn 서버 실행
"""


"""
간단한 FastAPI 애플리케이션
- Company/ProcessLine 조회 + Auth
"""

# ── ✅ Repo_Backend 경로를 모듈 검색 경로에 포함
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "Repo_Backend")
if os.path.isdir(os.path.join(BACKEND_DIR, "app")) and BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# 필요한 라이브러리들을 가져옵니다
from fastapi import FastAPI  # FastAPI 애플리케이션 생성용
from fastapi.middleware.cors import CORSMiddleware  # CORS 미들웨어

# 컨트롤러(라우터)
from app.controllers.auth_controller import router as auth_router # Company 컨트롤러 모듈
from app.controllers.company_controller import router as company_router
from app.controllers.process_line_controller import router as process_router # ✅ 추가: 인증 라우터
from app.controllers.production_grid_controller import router as production_grid_router
from app.controllers.defect_grid_controller import router as defect_grid_router
from app.controllers.defect_chart_controller import router as defect_chart_router
from app.controllers import downtime_grid_controller # Downtime(비가동) 컨트롤러 모듈
from app.controllers.downtime_chart_controller import router as downtime_chart_router # Downtime(비가동) 차트 컨트롤러 모듈
from app.controllers.user_grid_controller import router as user_grid_router
from app.controllers.production_chart_controller import router as production_chart_router
from app.controllers.inspection_grid_controller import router as inspection_grid_router # 검사내역 컨트롤러 모듈

from app.controllers.mold_cleaning_controller import router as mold_cleaning_router # 금형세척 라우터
from app.controllers.mold_shotCount_controller import router as mold_shotCount_router #금형타수 라우터
from app.controllers.mold_shot_check_controller import router as mold_shot_check_router #금형 Shot 체크 라우터

from app.controllers.inspection_chart_controller import router as inspection_chart_router # 검사 시스템 라우터
from app.controllers.mold_breakDown_controller import router as mold_breakDown_router #금형고장 라우터
from app.controllers.mold_chart_controller import router as mold_chart_router
from app.controllers.modal_controller import router as modal_router
# ============================================================================
# FastAPI 애플리케이션 생성 및 설정
# ============================================================================
# FastAPI 인스턴스를 생성합니다
# title: API 문서에 표시될 제목
# version: API 버전 정보
# description: API에 대한 상세 설명
app = FastAPI(
    # title="AJIN Company 조회 API",
    # version="1.0.0",
    # description="MariaDB에서 조회하는 API"

    title="AJIN Backend API",
    version="1.1.0",
    description="AJIN 스마트팩토리 백엔드 API (Company/ProcessLine 조회 + Auth)",
)

# ============================================================================
# CORS 미들웨어 설정
# ============================================================================
# Cross-Origin Resource Sharing (CORS) 미들웨어를 추가합니다
# 이는 웹 브라우저에서 다른 도메인의 API를 호출할 수 있게 해줍니다
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                     # ✅ 모든 도메인/포트 허용
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],    
)

# ============================================================================
# API 라우터 등록
# ============================================================================

# 조회 도메인
app.include_router(company_router, prefix="/smartFactory")
app.include_router(process_router, prefix="/smartFactory")
# 생산 관리
app.include_router(production_chart_router, prefix="/smartFactory")
app.include_router(production_grid_router, prefix="/smartFactory")
# 불량 공정
app.include_router(defect_chart_router, prefix="/smartFactory")
app.include_router(defect_grid_router, prefix="/smartFactory")
# 비가동
app.include_router(downtime_grid_controller.router, prefix="/smartFactory")
app.include_router(downtime_chart_router, prefix="/smartFactory")
# 사원 관리
app.include_router(user_grid_router, prefix="/smartFactory")  # ✅ /smartFactory/user_grid/...
# 금형 세척
app.include_router(mold_cleaning_router, prefix= "/smartFactory")
# 금형 타수
app.include_router(mold_shotCount_router, prefix= "/smartFactory")
# 금형 Shot 체크
app.include_router(mold_shot_check_router, prefix= "/smartFactory")
#금형 고장
app.include_router(mold_breakDown_router, prefix="/smartFactory")
# 초 중 종 검사내역
app.include_router(inspection_chart_router, prefix="/smartFactory")
app.include_router(inspection_grid_router, prefix="/smartFactory")
# 금형 그래프
app.include_router(mold_chart_router, prefix="/smartFactory")

app.include_router(modal_router, prefix='/smartFactory')

# ✅ 인증 도메인 (/auth/login, /auth/me 등)
app.include_router(auth_router)


# ============================================================================
# 기본 엔드포인트 정의
# ============================================================================
@app.get("/")  # 루트 경로 (/) 엔드포인트
async def root():
    """
    루트 엔드포인트 - API 기본 정보 제공
    
    이 엔드포인트는 API의 기본 정보와 사용법을 제공합니다.
    사용자가 루트 경로에 접근했을 때 API에 대한 개요를 확인할 수 있습니다.
    
    Returns:
        dict: API 기본 정보를 담은 딕셔너리
            - message: API 이름
            - description: API 설명
            - docs: API 문서 링크
            - company_endpoint: Company 조회 엔드포인트 경로
    """
    return {
        "message": "AJIN Backend 조회 API",                           # API 이름
        "description": "아진산업 스마트팩토리 백엔드 API 호출부 입니다",    # API 설명
        "docs": "/docs",                                              # Swagger UI 문서 링크
        "endpoints": {                                                # Member 조회 엔드포인트
            "auth_login": "POST /auth/login",                           
            "auth_me": "GET /auth/me",
            "company": "GET /smartFactory/ ...",
            "process_line": "GET /smartFactory/ ...",
        },
    }

    # return {
    #     "message": "AJIN Company 조회 API",                    # API 이름
    #     "description": "아진산업 스마트팩토리 백엔드 API 호출부 입니다",  # API 설명
    #     "docs": "/docs",                                       # Swagger UI 문서 링크
    #     "company_endpoint": "/smartFactory/"             # Company 조회 엔드포인트
    # }


# 헬스 체크 엔드포인트 추가
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API server is healthy"}

# 대시보드(Analytics) 더미 데이터 응답 (엔드포인트 추가)
@app.get("/analytics")
def analytics_stub():
    return {
        "kpis": {
            "visitors": 50873,
            "customers": 6452,
            "sales": 92000,
            "orders": 3240,
            "conversionRate": 0.207
        },
    }

# 혹시 프론트가 /api/analytics 로 호출하는 경우 대비
@app.get("/api/analytics")
def analytics_stub_compat():
    return analytics_stub()



# ============================================================================
# 애플리케이션 실행 (메인 모듈로 실행될 때만)
# ============================================================================
# 이 파일이 직접 실행될 때만 uvicorn 서버를 시작합니다
# 다른 모듈에서 import될 때는 실행되지 않습니다
if __name__ == "__main__":
    # uvicorn 라이브러리를 import합니다 (비동기 ASGI 서버)
    import uvicorn
    
    # uvicorn.run()을 사용하여 FastAPI 애플리케이션을 실행합니다
    uvicorn.run(
        "main:app",        # 실행할 애플리케이션 (main.py의 app 변수)
        host="0.0.0.0",    # 모든 네트워크 인터페이스에서 접근 허용
        port=8000,         # 서버 포트 번호
        reload=True         # 코드 변경 시 자동 재시작 (개발용)
    ) 