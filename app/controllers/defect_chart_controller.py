# from fastapi import APIRouter
# from pydantic import BaseModel
# from typing import Optional
# from app.services.defect_chart_service import defect_chart_service

# router = APIRouter(prefix="/defect_chart", tags=["defect"])

# # 요청 바디 (필터 공통)
# class DefectChartRequest(BaseModel):
#     start_date: Optional[str] = None    # 시작일 (YYYY-MM-DD)
#     end_date: Optional[str] = None      # 종료일 (YYYY-MM-DD)
#     workplace: Optional[str] = None     # 작업장
#     carModel: Optional[str] = None      # 차종
#     orderType: Optional[str] = None     # 수주유형
#     defectCode: Optional[str] = None    # 불량코드
#     defectType: Optional[str] = None    # 불량유형(부분검색 허용)
#     worker: Optional[str] = None        # 작업자
#     topN: Optional[int] = 10            # by_type 상위 개수

# @router.post("/kpis")
# def get_kpis(req: DefectChartRequest):
#     try:
#         data = defect_chart_service.get_kpis(req)
#         return {"message": "불량공정 KPI 조회 성공", "data": data}
#     except Exception as e:
#         return {"message": "불량공정 KPI 조회 실패", "error": str(e)}

# @router.post("/by_type")
# def get_by_type(req: DefectChartRequest):
#     try:
#         data = defect_chart_service.get_by_type(req)
#         return {"message": "불량유형 파레토 조회 성공", "count": len(data), "data": data}
#     except Exception as e:
#         return {"message": "불량유형 파레토 조회 실패", "error": str(e)}

# @router.post("/trend")
# def get_trend(req: DefectChartRequest):
#     try:
#         data = defect_chart_service.get_trend(req)
#         return {"message": "불량 추이 조회 성공", "count": len(data), "data": data}
#     except Exception as e:
#         return {"message": "불량 추이 조회 실패", "error": str(e)}

# @router.post("/stacked")
# def get_stacked(req: DefectChartRequest):
#     try:
#         data = defect_chart_service.get_stacked(req)
#         return {"message": "처분별 누적 추이 조회 성공", "count": len(data), "data": data}
#     except Exception as e:
#         return {"message": "처분별 누적 추이 조회 실패", "error": str(e)}



# app/controllers/defect_chart_controller.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.services.defect_chart_service import defect_chart_service

router = APIRouter(prefix="/defect_chart", tags=["defect"])

# 요청 바디 (필터 공통)
class DefectChartRequest(BaseModel):
    start_date: Optional[str] = None      # YYYY-MM-DD
    end_date: Optional[str] = None
    workplace: Optional[str] = None       # 작업장
    carModel: Optional[str] = None        # 차종
    orderType: Optional[str] = None       # 수주유형
    defectCode: Optional[str] = None      # 불량코드
    defectType: Optional[str] = None      # 불량유형(부분검색 허용)
    worker: Optional[str] = None          # 작업자
    # ▼ 추가: 품번/품명 필터
    itemCode: Optional[str] = None        # 자재번호(정확일치)
    itemName: Optional[str] = None        # 자재명(부분검색)
    topN: Optional[int] = 10              # by_type 상위 개수

@router.get("/item-codes")
def get_item_codes(
    workplace: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    defectType: Optional[str] = None,
):
    """불량 테이블에서 자재번호/자재명 목록(중복 제거)"""
    try:
        data = defect_chart_service.get_item_codes(
            workplace=workplace, start_date=start_date, end_date=end_date, defectType=defectType
        )
        return {"message": "자재번호 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자재번호 조회 실패: {e}")

@router.post("/kpis")
def get_kpis(req: DefectChartRequest):
    try:
        data = defect_chart_service.get_kpis(req)
        return {"message": "불량 KPI 조회 성공", "data": data}
    except Exception as e:
        return {"message": "불량 KPI 조회 실패", "error": str(e)}

@router.post("/by_type")
def get_by_type(req: DefectChartRequest):
    try:
        data = defect_chart_service.get_by_type(req)
        return {"message": "불량유형 파레토 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "불량유형 파레토 조회 실패", "error": str(e)}

@router.post("/trend")
def get_trend(req: DefectChartRequest):
    try:
        data = defect_chart_service.get_trend(req)
        return {"message": "불량 추이 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "불량 추이 조회 실패", "error": str(e)}

@router.post("/stacked")
def get_stacked(req: DefectChartRequest):
    try:
        data = defect_chart_service.get_stacked(req)
        return {"message": "처분별 누적 추이 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "처분별 누적 추이 조회 실패", "error": str(e)}
