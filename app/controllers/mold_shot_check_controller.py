from fastapi import APIRouter
from typing import List, Optional
from app.services.mold_shot_check_service import Mold_shot_check_service
from app.models.moldShotCount import moldShotCount

router = APIRouter(prefix="/mold_shot_check", tags=["mold"])
service = Mold_shot_check_service()

@router.post("/list")
def get_mold_shot_check_list(request: moldShotCount):
    try:
        data = service.get_moldShotCheck_list(request)
        return {
            "message": "금형 Shot 체크 데이터 조회 성공",
            "count": len(data),
            "data": data
        }
    except Exception as e:
        print(f"금형 Shot 체크 데이터 조회 중 오류 발생: {str(e)}")
        return {
            "message": "금형 Shot 체크 데이터 조회 실패",
            "error": str(e)
        }





