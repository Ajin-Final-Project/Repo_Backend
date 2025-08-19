from fastapi import APIRouter
from typing import List,Optional
from app.services.mold_cleaning_service import Mold_cleaning_service
from app.models.mold_cleaning import MoldCleaningCycleRequest


router = APIRouter(prefix="/mold_cleaning", tags=["mold"])
service = Mold_cleaning_service()


    
@router.post("/list")
def get_process_line(request: MoldCleaningCycleRequest):
    try:
        data = service.get_moldCleaning_list(request)
        return {
            "message": "금형세척 테이블 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"금형세척 테이블 조회 중 오류 발생: {str(e)}")
        return {
            "message": "금형세척 테이블 조회 실패",
            "error": str(e)
        }





