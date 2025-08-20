from fastapi import APIRouter
from typing import List,Optional
from app.services.mold_breakDown_service import Mold_breakDown_service
from app.models.mold_BreakDown import MoldBreakdownRequest


router = APIRouter(prefix="/mold_breakDown", tags=["mold"])
service = Mold_breakDown_service()


    
@router.post("/list")
def get_moldBreakDown_list(request: MoldBreakdownRequest):
    try:
        data = service.get_moldBreakDown_list(request)
        return {
            "message": "금형타수 테이블 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"금형타수 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "금형세척 테이블 조회 실패",
            "error": str(e)
        }





