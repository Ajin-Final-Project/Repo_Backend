from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.inspection_chart_service import inspection_chart_service

router = APIRouter(prefix="/inspection_chart", tags=["inspection"])

# 공통 필터
class InspectionChartRequest(BaseModel):
    start_date: Optional[str] = None     # YYYY-MM-DD
    end_date: Optional[str] = None
    factory: Optional[str] = None        # 공장
    process: Optional[str] = None        # 공정
    equipment: Optional[str] = None      # ✅ 설비
    partNo: Optional[str] = None         # 품번 (부분검색 허용)
    workType: Optional[str] = None       # 작업구분(초/중/종)
    inspType: Optional[str] = None       # 검사구분(자동/자주 등)
    shiftType: Optional[str] = None      # ✅ 주야구분
    item: Optional[str] = None           # 검사항목명 (부분검색 허용)
    topN: Optional[int] = 5              # 기본 TopN = 5

# -----------------------------
# ✅ 통합 대시보드 엔드포인트
# -----------------------------
@router.post("/dashboard")
def get_dashboard(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_dashboard(req)
        return {"message": "대시보드 통합 조회 성공", "data": data}
    except Exception as e:
        return {"message": "대시보드 통합 조회 실패", "error": str(e)}

# (개별 엔드포인트 하위 호환)
@router.post("/kpis")
def get_kpis(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_kpis(req)
        return {"message": "검사 KPI 조회 성공", "data": data}
    except Exception as e:
        return {"message": "검사 KPI 조회 실패", "error": str(e)}

@router.post("/by_item")
def get_by_item(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_by_item(req)
        return {"message": "검사항목 파레토 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "검사항목 파레토 조회 실패", "error": str(e)}

@router.post("/trend")
def get_trend(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_trend(req)
        return {"message": "검사 건수 추이 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "검사 건수 추이 조회 실패", "error": str(e)}

@router.post("/stacked")
def get_stacked(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_stacked(req)
        return {"message": "검사구분별 누적 추이 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "검사구분별 누적 추이 조회 실패", "error": str(e)}

# TopN 인사이트
@router.post("/by_part")
def get_by_part(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_by_part(req)
        return {"message": "품번 TopN 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "품번 TopN 조회 실패", "error": str(e)}

@router.post("/by_process")
def get_by_process(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_by_process(req)
        return {"message": "공정 TopN 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "공정 TopN 조회 실패", "error": str(e)}

@router.post("/by_machine")
def get_by_machine(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_by_machine(req)
        return {"message": "설비 TopN 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "설비 TopN 조회 실패", "error": str(e)}

# 스루풋/주야/모멘텀
@router.post("/throughput")
def get_throughput(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_throughput(req)
        return {"message": "스루풋 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "스루풋 조회 실패", "error": str(e)}

@router.post("/shift")
def get_shift(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_shift(req)
        return {"message": "주/야 추이 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "주/야 추이 조회 실패", "error": str(e)}

@router.post("/momentum")
def get_momentum(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_momentum_parts(req)
        return {"message": "모멘텀 품번 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "모멘텀 품번 조회 실패", "error": str(e)}

# 인사이트
@router.post("/weekday_profile")
def get_weekday_profile(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_weekday_profile(req)
        return {"message": "요일 패턴 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "요일 패턴 조회 실패", "error": str(e)}

# 공정 기준(호환)
@router.post("/intensity_by_process")
def get_intensity_by_process(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_intensity_by_process(req)
        return {"message": "공정별 검사강도 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "공정별 검사강도 조회 실패", "error": str(e)}

@router.post("/shift_imbalance_process")
def get_shift_imbalance_process(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_shift_imbalance_process(req)
        return {"message": "공정별 주/야 불균형 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "공정별 주/야 불균형 조회 실패", "error": str(e)}

# 설비 기준(신규)
@router.post("/intensity_by_machine")
def get_intensity_by_machine(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_intensity_by_machine(req)
        return {"message": "설비별 검사강도 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "설비별 검사강도 조회 실패", "error": str(e)}

@router.post("/shift_imbalance_machine")
def get_shift_imbalance_machine(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_shift_imbalance_machine(req)
        return {"message": "설비별 주/야 불균형 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "설비별 주/야 불균형 조회 실패", "error": str(e)}

@router.post("/anomaly_days")
def get_anomaly_days(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_anomaly_days(req)
        return {"message": "이상치(스파이크) 조회 성공", "count": len(data), "data": data}
    except Exception as e:
        return {"message": "이상치(스파이크) 조회 실패", "error": str(e)}

@router.post("/pareto_concentration")
def get_pareto_concentration(req: InspectionChartRequest):
    try:
        data = inspection_chart_service.get_pareto_concentration(req)
        return {"message": "집중도(TopN 비중) 조회 성공", "data": data}
    except Exception as e:
        return {"message": "집중도(TopN 비중) 조회 실패", "error": str(e)}

# 드롭다운 옵션
@router.post("/options/factories")
def list_factories(req: InspectionChartRequest):
    try:
        return {"message": "공장 옵션 조회 성공", "data": inspection_chart_service.list_factories(req)}
    except Exception as e:
        return {"message": "공장 옵션 조회 실패", "error": str(e)}

@router.post("/options/processes")
def list_processes(req: InspectionChartRequest):
    try:
        return {"message": "공정 옵션 조회 성공", "data": inspection_chart_service.list_processes(req)}
    except Exception as e:
        return {"message": "공정 옵션 조회 실패", "error": str(e)}

@router.post("/options/equipments")
def list_equipments(req: InspectionChartRequest):
    try:
        return {"message": "설비 옵션 조회 성공", "data": inspection_chart_service.list_equipments(req)}
    except Exception as e:
        return {"message": "설비 옵션 조회 실패", "error": str(e)}

@router.post("/options/parts")
def list_parts(req: InspectionChartRequest):
    try:
        return {"message": "품번 옵션 조회 성공", "data": inspection_chart_service.list_parts(req)}
    except Exception as e:
        return {"message": "품번 옵션 조회 실패", "error": str(e)}

@router.post("/options/items")
def list_items(req: InspectionChartRequest):
    try:
        return {"message": "검사항목 옵션 조회 성공", "data": inspection_chart_service.list_items(req)}
    except Exception as e:
        return {"message": "검사항목 옵션 조회 실패", "error": str(e)}

# ✅ 연도 옵션
@router.post("/options/years")
def list_years(req: InspectionChartRequest):
    try:
        return {"message": "연도 옵션 조회 성공", "data": inspection_chart_service.list_years(req)}
    except Exception as e:
        return {"message": "연도 옵션 조회 실패", "error": str(e)}
