# # """
# # 간단한 FastAPI 애플리케이션
# # - Company/ProcessLine 조회 + Auth
# # """

# # # ── ✅ Repo_Backend 경로를 모듈 검색 경로에 포함
# # import os, sys
# # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# # BACKEND_DIR = os.path.join(BASE_DIR, "Repo_Backend")
# # if os.path.isdir(os.path.join(BACKEND_DIR, "app")) and BACKEND_DIR not in sys.path:
# #     sys.path.insert(0, BACKEND_DIR)

# # from fastapi import FastAPI
# # from fastapi.middleware.cors import CORSMiddleware

# # # 컨트롤러(라우터)
# # from app.controllers.auth_controller import router as auth_router
# # from app.controllers.company_controller import router as company_router
# # from app.controllers.process_line_controller import router as process_router
# # from app.controllers.production_grid_controller import router as production_grid_router
# # from app.controllers.defect_grid_controller import router as defect_grid_router
# # from app.controllers.defect_chart_controller import router as defect_chart_router
# # from app.controllers import downtime_grid_controller
# # from app.controllers.downtime_chart_controller import router as downtime_chart_router
# # from app.controllers.user_grid_controller import router as user_grid_router
# # from app.controllers.production_chart_controller import router as production_chart_router
# # from app.controllers.inspection_grid_controller import router as inspection_grid_router

# # from app.controllers.mold_cleaning_controller import router as mold_cleaning_router
# # # from app.controllers.mold_shotCount_controller import router as mold_shotCount_router
# # from app.controllers.mold_shot_check_controller import router as mold_shot_check_router

# # # 검사 시스템 라우터
# # from app.controllers.inspection_chart_controller import router as inspection_chart_router
# # from app.controllers.inspection_grid_controller import router as inspection_grid_router
# # from app.controllers.inspection_item_modal_controller import router as inspection_item_modal_router

# # from app.controllers.mold_breakDown_controller import router as mold_breakDown_router
# # from app.controllers.mold_chart_controller import router as mold_chart_router
# # from app.controllers.modal_controller import router as modal_router

# # from app.controllers.product_forecast_controller import router as product_forecast_router
# # from app.controllers.bottleneck_overview_controller import router as bottleneck_overview_router

# # # ============================================================================

# # app = FastAPI(
# #     title="AJIN Backend API",
# #     version="1.1.0",
# #     description="AJIN 스마트팩토리 백엔드 API (Company/ProcessLine 조회 + Auth)",
# # )

# # # CORS
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=False,
# #     allow_methods=["*"],
# #     allow_headers=["*"],  # ← 필요 시 전체 허용
# # )

# # # ============================================================================

# # # 조회 도메인
# # app.include_router(company_router, prefix="/smartFactory")
# # app.include_router(process_router, prefix="/smartFactory")

# # # 생산 관리
# # app.include_router(production_chart_router, prefix="/smartFactory")
# # app.include_router(production_grid_router, prefix="/smartFactory")

# # # 불량 공정
# # app.include_router(defect_chart_router, prefix="/smartFactory")
# # app.include_router(defect_grid_router, prefix="/smartFactory")

# # # 비가동
# # app.include_router(downtime_grid_controller.router, prefix="/smartFactory")
# # app.include_router(downtime_chart_router, prefix="/smartFactory")

# # # 사원 관리
# # app.include_router(user_grid_router, prefix="/smartFactory")

# # # 금형 세척
# # app.include_router(mold_cleaning_router, prefix="/smartFactory")
# # # app.include_router(mold_shotCount_router, prefix="/smartFactory")
# # app.include_router(mold_shot_check_router, prefix="/smartFactory")

# # # 금형 고장
# # app.include_router(mold_breakDown_router, prefix="/smartFactory")

# # # 검사(초/중/종)
# # app.include_router(inspection_chart_router, prefix="/smartFactory")
# # app.include_router(inspection_grid_router, prefix="/smartFactory")
# # app.include_router(inspection_item_modal_router, prefix="/smartFactory")

# # # 금형 그래프
# # app.include_router(mold_chart_router, prefix="/smartFactory")
# # app.include_router(modal_router, prefix='/smartFactory')

# # # AI (생산량/병목)
# # app.include_router(product_forecast_router, prefix="/smartFactory")
# # app.include_router(bottleneck_overview_router, prefix="/smartFactory")

# # # 인증
# # app.include_router(auth_router)

# # # ============================================================================

# # @app.get("/")
# # async def root():
# #     return {
# #         "message": "AJIN Backend 조회 API",
# #         "description": "아진산업 스마트팩토리 백엔드 API 호출부 입니다",
# #         "docs": "/docs",
# #         "endpoints": {
# #             "auth_login": "POST /auth/login",
# #             "auth_me": "GET /auth/me",
# #             "company": "GET /smartFactory/ ...",
# #             "process_line": "GET /smartFactory/ ...",
# #         },
# #     }

# # @app.get("/health")
# # def health_check():
# #     return {"status": "ok", "message": "API server is healthy"}

# # @app.get("/analytics")
# # def analytics_stub():
# #     return {
# #         "kpis": {
# #             "visitors": 50873,
# #             "customers": 6452,
# #             "sales": 92000,
# #             "orders": 3240,
# #             "conversionRate": 0.207
# #         },
# #     }

# # @app.get("/api/analytics")
# # def analytics_stub_compat():
# #     return analytics_stub()

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run(
# #         "main:app",
# #         host="0.0.0.0",
# #         port=8000,
# #         reload=True
# #     )


# """
# 간단한 FastAPI 애플리케이션
# - Company/ProcessLine 조회 + Auth
# """

# # ── ✅ Repo_Backend 경로를 모듈 검색 경로에 포함
# import os, sys
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BACKEND_DIR = os.path.join(BASE_DIR, "Repo_Backend")
# if os.path.isdir(os.path.join(BACKEND_DIR, "app")) and BACKEND_DIR not in sys.path:
#     sys.path.insert(0, BACKEND_DIR)

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# # 컨트롤러(라우터)
# from app.controllers.auth_controller import router as auth_router
# from app.controllers.company_controller import router as company_router
# from app.controllers.process_line_controller import router as process_router
# from app.controllers.production_grid_controller import router as production_grid_router
# from app.controllers.defect_grid_controller import router as defect_grid_router
# from app.controllers.defect_chart_controller import router as defect_chart_router
# from app.controllers import downtime_grid_controller
# from app.controllers.downtime_chart_controller import router as downtime_chart_router
# from app.controllers.user_grid_controller import router as user_grid_router
# from app.controllers.production_chart_controller import router as production_chart_router

# # 검사 시스템 라우터
# from app.controllers.inspection_chart_controller import router as inspection_chart_router
# from app.controllers.inspection_grid_controller import router as inspection_grid_router
# from app.controllers.inspection_item_modal_controller import router as inspection_item_modal_router

# from app.controllers.mold_cleaning_controller import router as mold_cleaning_router
# from app.controllers.mold_shot_check_controller import router as mold_shot_check_router
# from app.controllers.mold_breakDown_controller import router as mold_breakDown_router
# from app.controllers.mold_chart_controller import router as mold_chart_router
# from app.controllers.modal_controller import router as modal_router

# from app.controllers.product_forecast_controller import router as product_forecast_router
# from app.controllers.bottleneck_overview_controller import router as bottleneck_overview_router

# # ============================================================================

# app = FastAPI(
#     title="AJIN Backend API",
#     version="1.1.0",
#     description="AJIN 스마트팩토리 백엔드 API (Company/ProcessLine 조회 + Auth)",
# )

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],  # ← 필요 시 전체 허용
# )

# # ============================================================================

# # 조회 도메인
# app.include_router(company_router, prefix="/smartFactory")
# app.include_router(process_router, prefix="/smartFactory")

# # 생산 관리
# app.include_router(production_chart_router, prefix="/smartFactory")
# app.include_router(production_grid_router, prefix="/smartFactory")

# # 불량 공정
# app.include_router(defect_chart_router, prefix="/smartFactory")
# app.include_router(defect_grid_router, prefix="/smartFactory")

# # 비가동
# app.include_router(downtime_grid_controller.router, prefix="/smartFactory")
# app.include_router(downtime_chart_router, prefix="/smartFactory")

# # 사원 관리
# app.include_router(user_grid_router, prefix="/smartFactory")

# # 금형 세척
# app.include_router(mold_cleaning_router, prefix="/smartFactory")
# app.include_router(mold_shot_check_router, prefix="/smartFactory")

# # 금형 고장
# app.include_router(mold_breakDown_router, prefix="/smartFactory")

# # 검사(초/중/종)
# app.include_router(inspection_chart_router, prefix="/smartFactory")
# app.include_router(inspection_grid_router, prefix="/smartFactory")
# app.include_router(inspection_item_modal_router, prefix="/smartFactory")

# # 금형 그래프
# app.include_router(mold_chart_router, prefix="/smartFactory")
# app.include_router(modal_router, prefix='/smartFactory')

# # AI (생산량/병목)
# app.include_router(product_forecast_router, prefix="/smartFactory")
# app.include_router(bottleneck_overview_router, prefix="/smartFactory")

# # 인증
# app.include_router(auth_router)

# # ============================================================================

# @app.get("/")
# async def root():
#     return {
#         "message": "AJIN Backend 조회 API",
#         "description": "아진산업 스마트팩토리 백엔드 API 호출부 입니다",
#         "docs": "/docs",
#         "endpoints": {
#             "auth_login": "POST /auth/login",
#             "auth_me": "GET /auth/me",
#             "company": "GET /smartFactory/ ...",
#             "process_line": "GET /smartFactory/ ...",
#         },
#     }

# @app.get("/health")
# def health_check():
#     return {"status": "ok", "message": "API server is healthy"}

# @app.get("/analytics")
# def analytics_stub():
#     return {
#         "kpis": {
#             "visitors": 50873,
#             "customers": 6452,
#             "sales": 92000,
#             "orders": 3240,
#             "conversionRate": 0.207
#         },
#     }

# @app.get("/api/analytics")
# def analytics_stub_compat():
#     return analytics_stub()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True
#     )


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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 컨트롤러(라우터)
from app.controllers.auth_controller import router as auth_router
from app.controllers.company_controller import router as company_router
from app.controllers.process_line_controller import router as process_router
from app.controllers.production_grid_controller import router as production_grid_router
from app.controllers.defect_grid_controller import router as defect_grid_router
from app.controllers.defect_chart_controller import router as defect_chart_router
from app.controllers.downtime_grid_controller import router as downtime_grid_router
from app.controllers.downtime_chart_controller import router as downtime_chart_router
from app.controllers.user_grid_controller import router as user_grid_router
from app.controllers.production_chart_controller import router as production_chart_router

# 검사 시스템 라우터
from app.controllers.inspection_chart_controller import router as inspection_chart_router
from app.controllers.inspection_grid_controller import router as inspection_grid_router
from app.controllers.inspection_item_modal_controller import router as inspection_item_modal_router

from app.controllers.mold_cleaning_controller import router as mold_cleaning_router
from app.controllers.mold_shot_check_controller import router as mold_shot_check_router
from app.controllers.mold_breakDown_controller import router as mold_breakDown_router
from app.controllers.mold_chart_controller import router as mold_chart_router
from app.controllers.modal_controller import router as modal_router

from app.controllers.product_forecast_controller import router as product_forecast_router
from app.controllers.bottleneck_overview_controller import router as bottleneck_overview_router

# RAG 챗봇 라우터
from app.controllers.chat_controller import router as chat_router

# ============================================================================

app = FastAPI(
    title="AJIN Backend API",
    version="1.1.0",
    description="AJIN 스마트팩토리 백엔드 API (Company/ProcessLine 조회 + Auth)",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

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
app.include_router(downtime_grid_router, prefix="/smartFactory")
app.include_router(downtime_chart_router, prefix="/smartFactory")

# 사원 관리
app.include_router(user_grid_router, prefix="/smartFactory")

# 금형 세척
app.include_router(mold_cleaning_router, prefix="/smartFactory")
app.include_router(mold_shot_check_router, prefix="/smartFactory")

# 금형 고장
app.include_router(mold_breakDown_router, prefix="/smartFactory")

# 검사(초/중/종)
app.include_router(inspection_chart_router, prefix="/smartFactory")
app.include_router(inspection_grid_router, prefix="/smartFactory")
app.include_router(inspection_item_modal_router, prefix="/smartFactory")

# 금형 그래프
app.include_router(mold_chart_router, prefix="/smartFactory")
app.include_router(modal_router, prefix='/smartFactory')

# AI (생산량/병목)
app.include_router(product_forecast_router, prefix="/smartFactory")
app.include_router(bottleneck_overview_router, prefix="/smartFactory")

# 인증
app.include_router(auth_router)

# RAG 챗봇
app.include_router(chat_router, prefix="/smartFactory")

# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "AJIN Backend 조회 API",
        "description": "아진산업 스마트팩토리 백엔드 API 호출부 입니다",
        "docs": "/docs",
        "endpoints": {
            "auth_login": "POST /auth/login",
            "auth_me": "GET /auth/me",
            "company": "GET /smartFactory/ ...",
            "process_line": "GET /smartFactory/ ...",
            "rag_chat": "POST /chat/chat",
            "rag_health": "GET /chat/health"
        },
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API server is healthy"}

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

@app.get("/api/analytics")
def analytics_stub_compat():
    return analytics_stub()

def initialize_rag_system():
    """RAG 시스템 초기화 - ChromaDB 컬렉션이 없으면 생성"""
    try:
        import chromadb
        from app.config.settings import CHROMA_PATH
        
        # ChromaDB 클라이언트 초기화
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        
        # ajin_unified 컬렉션이 존재하는지 확인
        try:
            collection = chroma_client.get_collection("ajin_unified")
            print("✅ RAG 컬렉션이 이미 존재합니다.")
            return True
        except:
            print("⚠️  RAG 컬렉션이 없습니다. 데이터 인덱싱을 시작합니다...")
            
            # 데이터 인덱싱 실행
            from app.services.rag_service import index_unified_docs
            index_unified_docs()
            print("✅ RAG 데이터 인덱싱이 완료되었습니다.")
            return True
            
    except Exception as e:
        print(f"⚠️  RAG 시스템 초기화 중 오류: {e}")
        print("테스트 모드로 실행됩니다.")
        return False

if __name__ == "__main__":
    # RAG 시스템 초기화 => chromadb에 데이터 없을떄만 새로만듬
    initialize_rag_system()
    
    # FastAPI 서버 실행
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
