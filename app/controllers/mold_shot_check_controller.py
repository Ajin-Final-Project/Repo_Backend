from fastapi import APIRouter
from typing import List, Optional
from app.services.model_shotCount_service import Mold_shotCount_service
from app.models.moldShotCount import moldShotCount

router = APIRouter(prefix="/mold_shot_check", tags=["mold"])
service = Mold_shotCount_service()

@router.post("/list")
def get_mold_shot_check_list(request: moldShotCount):
    try:
        data = service.get_moldShotCount_list(request)
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





