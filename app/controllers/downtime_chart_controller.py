# app/controllers/downtime_chart_controller.py
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Body
from app.services.downtime_chart_service import downtime_chart_service
from app.models.downtimeGrid import DowntimeGridResquest

router = APIRouter(prefix="/downtime_chart", tags=["downtime"])

# -------- GET /item-codes : 프론트 쿼리스트링과 1:1 매핑 --------
@router.get("/item-codes")
def get_item_codes(
    workplace: Optional[str] = None,
    start_work_date: Optional[str] = None,
    end_work_date: Optional[str] = None,
):
    try:
        req = DowntimeGridResquest(
            workplace=workplace,
            start_work_date=start_work_date,
            end_work_date=end_work_date,
        )
        data = downtime_chart_service.get_item_codes(req)
        return {"message": "자재번호 조회 성공", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자재번호 조회 실패: {e}")

# -------- POST /summary : top은 쿼리파라미터로 (프론트에서 ?top=3 전송) --------
@router.post("/summary")
def get_summary(req: DowntimeGridResquest, top: int = Query(3, ge=1, le=10)):
    try:
        data = downtime_chart_service.get_summary(req, top_n=top)
        return {"message": "summary 조회 성공", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"summary 조회 실패: {e}")

# -------- POST /monthly --------
@router.post("/monthly")
def get_monthly(req: DowntimeGridResquest):
    try:
        data = downtime_chart_service.get_monthly(req)
        return {"message": "monthly 조회 성공", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"monthly 조회 실패: {e}")

# -------- POST /pie : 프론트가 body로 top/withOthers 보내도 파싱되도록 Body(...) 사용 --------
@router.post("/pie")
def get_pie(request: DowntimeGridResquest, top:int=5, withOthers:bool=True):
    try:
        data = downtime_chart_service.get_pie(request, top=top, withOthers=withOthers)
        return {"message": "pie 조회 성공", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"pie 조회 실패: {e}")

@router.post("/top-notes")
def get_top_notes(request: DowntimeGridResquest, limit:int=10):
    try:
        data = downtime_chart_service.get_top_notes(request, limit=limit)
        return {"message": "top-notes 조회 성공", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"top-notes 조회 실패: {e}")

@router.post("/actions")
def get_actions(request: DowntimeGridResquest, limit:int=8):
    try:
        data = downtime_chart_service.get_actions(request, limit=limit)
        return {"message": "actions 조회 성공", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"actions 조회 실패: {e}")

@router.post("/causes")
def get_causes(request: DowntimeGridResquest, limit:int=8):
    try:
        data = downtime_chart_service.get_causes(request, limit=limit)
        return {"message": "causes 조회 성공", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"causes 조회 실패: {e}")