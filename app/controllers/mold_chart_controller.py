from fastapi import APIRouter, HTTPException
from app.models.mold_BreakDown import MoldBreakdownRequest
from app.services.mold_chart_service import mold_chart_service

router = APIRouter(prefix="/mold-chart", tags=["mold"])

@router.post("/work-count")
async def get_mold_work_count_chart(req: MoldBreakdownRequest):
    """
    금형 설비별 작업횟수 차트 데이터 조회
    """
    try:
        result = mold_chart_service.get_mold_workCount_chart(req)
        return {
            "success": True,
            "data": result,
            "message": "금형 설비별 작업횟수 차트 데이터를 성공적으로 조회했습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"작업횟수 차트 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/runtime")
async def get_runtime_chart(req: MoldBreakdownRequest):
    """
    금형 설비별 가동시간 차트 데이터 조회
    """
    try:
        result = mold_chart_service.get_runtime_chart(req)
        return {
            "success": True,
            "data": result,
            "message": "금형 설비별 가동시간 차트 데이터를 성공적으로 조회했습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가동시간 차트 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/summarize")
async def get_summarize_data(req: MoldBreakdownRequest):
    """
    특정 설비의 요약 데이터 조회
    """
    try:
        result = mold_chart_service.get_summerize_data(req)
        return {
            "success": True,
            "data": result,
            "message": "설비 요약 데이터를 성공적으로 조회했습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 데이터 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/breakdown")
async def get_mold_breakdown_chart(req: MoldBreakdownRequest):
    """
    특정 설비의 고장 차트 데이터 조회
    """
    try:
        result = mold_chart_service.get_mold_breakDown_chart(req)
        return {
            "success": True,
            "data": result,
            "message": "금형 고장 차트 데이터를 성공적으로 조회했습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"고장 차트 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/breakdown-pie-top10")
async def get_mold_breakdown_pie_top10(req: MoldBreakdownRequest):
    """
    금형 고장 TOP 10 파이 차트 데이터 조회
    """
    try:
        result = mold_chart_service.get_mold_breakDown_pie_top10(req)
        return {
            "success": True,
            "data": result,
            "message": "금형 고장 TOP 10 파이 차트 데이터를 성공적으로 조회했습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"고장 TOP 10 파이 차트 조회 중 오류가 발생했습니다: {str(e)}")






