from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.defect_chart_service import defect_chart_service

router = APIRouter(prefix="/defect_chart", tags=["defect"])

# 요청 바디 (필터 공통)
class DefectChartRequest(BaseModel):
    start_date: Optional[str] = None    # 시작일 (YYYY-MM-DD)
    end_date: Optional[str] = None      # 종료일 (YYYY-MM-DD)
    workplace: Optional[str] = None     # 작업장
    carModel: Optional[str] = None      # 차종
    orderType: Optional[str] = None     # 수주유형
    defectCode: Optional[str] = None    # 불량코드
    defectType: Optional[str] = None    # 불량유형(부분검색 허용)
    worker: Optional[str] = None        # 작업자
    topN: Optional[int] = 10            # by_type 상위 개수

@router.post("/kpis")
def get_kpis(req: DefectChartRequest):
    try:
        data = defect_chart_service.get_kpis(req)
        return {"message": "불량공정 KPI 조회 성공", "data": data}
    except Exception as e:
        return {"message": "불량공정 KPI 조회 실패", "error": str(e)}

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
